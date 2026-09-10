"""
Feature engineering and synthetic data generator for ML regressor training.
Standardizes dataset value rows before encoding features.
"""

import random
import pandas as pd
import numpy as np
from eligibility_engine import matches, EDU_LEVEL_MAP, INSTITUTION_MAP

GENDERS = ["Male", "Female", "Transgender"]
CASTES = ["General", "OBC", "SC", "ST", "Minority"]
EDUCATION_LEVELS = [
    "School", "Senior Secondary", "Diploma", "Undergraduate",
    "Postgraduate", "PhD"
]
COURSES = [
    "General/Any", "Engineering", "Medical", "Arts", "Science",
    "Commerce", "Law", "Management", "Vocational/ITI"
]
INSTITUTION_TYPES = ["Government", "Private", "Aided"]


def generate_citizens(n, states, seed=42):
    """Generate synthetic student profiles for model training."""
    rng = random.Random(seed)
    states = [s for s in states if s and s != "All India"]

    citizens = []
    for i in range(n):
        citizens.append({
            "citizen_id": i,
            "age": rng.randint(5, 30),
            "gender": rng.choice(GENDERS),
            "caste_category": rng.choice(CASTES),
            "income": rng.choice([
                0, 50000, 90000, 120000, 150000, 200000, 250000,
                300000, 400000, 600000, 800000, 1200000
            ]),
            "state": rng.choice(states) if states else "Maharashtra",
            "education_level": rng.choice(EDUCATION_LEVELS),
            "course": rng.choice(COURSES),
            "marks_percentage": rng.choice([
                35, 40, 45, 50, 55, 60, 65, 70, 75,
                80, 85, 90, 95
            ]),
            "institution_type": rng.choice(INSTITUTION_TYPES),
        })
    return pd.DataFrame(citizens)


def build_training_pairs(citizens_df, schemes_df):
    """Create student-scheme pairs using standard row values."""
    rows = []

    for _, c in citizens_df.iterrows():
        for _, s in schemes_df.iterrows():
            state_ok = (
                s["level"] != "State"
                or str(s["state"]).strip().lower() == str(c["state"]).strip().lower()
            )
            gender_ok = matches(s["gender"], c["gender"])
            caste_ok = matches(s["caste_category"], c["caste_category"])
            age_ok = s["min_age"] <= c["age"] <= s["max_age"]
            income_ok = s["max_income"] == -1 or c["income"] <= s["max_income"]
            edu_ok = matches(s["education_level"], c["education_level"])
            course_ok = matches(s["course"], c["course"])
            marks_ok = s["min_marks"] == 0 or c["marks_percentage"] >= s["min_marks"]
            inst_ok = matches(s["institution_type"], c["institution_type"])

            eligible = int(
                state_ok and gender_ok and caste_ok and age_ok
                and income_ok and edu_ok and course_ok and marks_ok and inst_ok
            )

            if eligible:
                course_bonus = (
                    0.20 if s["course"] not in ["All", "All/General", "General/Any"]
                    and matches(s["course"], c["course"]) else 0.0
                )
                income_bonus = (
                    0.15 if s["max_income"] == -1
                    else 0.15 * max(
                        0, (s["max_income"] - c["income"]) / max(s["max_income"], 1)
                    )
                )
                marks_bonus = (
                    0.10 if s["min_marks"] == 0
                    else 0.15 * min(
                        max(0, (c["marks_percentage"] - s["min_marks"]) / 100) * 2,
                        1.0
                    )
                )
                age_span = max(s["max_age"] - s["min_age"], 1)
                age_center = (s["min_age"] + s["max_age"]) / 2
                age_bonus = 0.15 * (
                    1 - min(abs(c["age"] - age_center) / age_span, 1)
                )
                edu_bonus = (
                    0.10 if s["education_level"] != "All"
                    and matches(s["education_level"], c["education_level"]) else 0.0
                )
                caste_bonus = (
                    0.10 if s["caste_category"] != "All"
                    and matches(s["caste_category"], c["caste_category"]) else 0.0
                )
                inst_bonus = (
                    0.05 if s["institution_type"] != "All"
                    and matches(s["institution_type"], c["institution_type"]) else 0.0
                )
                state_bonus = 0.10 if s["level"] == "State" else 0.05

                match_score = min(
                    1.0,
                    course_bonus + income_bonus + marks_bonus + age_bonus
                    + edu_bonus + caste_bonus + inst_bonus + state_bonus
                )
            else:
                match_score = 0.0

            rows.append({
                "age": c["age"],
                "gender": c["gender"],
                "caste_category": c["caste_category"],
                "income": c["income"],
                "state": c["state"],
                "education_level": c["education_level"],
                "course": c["course"],
                "marks_percentage": c["marks_percentage"],
                "institution_type": c["institution_type"],
                "scheme_id": s["scheme_id"],
                "scheme_gender": s["gender"],
                "scheme_caste": s["caste_category"],
                "scheme_min_age": s["min_age"],
                "scheme_max_age": s["max_age"],
                "scheme_max_income": s["max_income"],
                "scheme_education_level": s["education_level"],
                "scheme_course": s["course"],
                "scheme_min_marks": s["min_marks"],
                "scheme_institution_type": s["institution_type"],
                "scheme_level": s["level"],
                "eligible": eligible,
                "match_score": match_score,
            })

    return pd.DataFrame(rows)


def encode_features(pairs_df):
    """One-hot/numeric encode student-scheme pairs for sklearn."""
    df = pairs_df.copy()

    # Map raw dataset value codes to standardized UI strings for cleaner encoding
    df["scheme_education_level"] = df["scheme_education_level"].apply(
        lambda x: EDU_LEVEL_MAP.get(str(x).strip().lower(), x)
    )
    df["scheme_institution_type"] = df["scheme_institution_type"].apply(
        lambda x: INSTITUTION_MAP.get(str(x).strip().lower(), x)
    )

    cat_cols = [
        "gender", "caste_category", "education_level", "course",
        "institution_type", "scheme_gender", "scheme_caste",
        "scheme_education_level", "scheme_course",
        "scheme_institution_type", "scheme_level"
    ]
    cat_cols = [c for c in cat_cols if c in df.columns]
    df = pd.get_dummies(df, columns=cat_cols)

    df["income_gap"] = df["scheme_max_income"].replace(-1, 2_000_000) - df["income"]
    df["marks_gap"] = df["marks_percentage"] - df["scheme_min_marks"].clip(lower=0)
    df["age_in_band"] = (
        (df["age"] >= df["scheme_min_age"]) & (df["age"] <= df["scheme_max_age"])
    ).astype(int)

    df = df.drop(
        columns=[c for c in ["state", "scheme_id"] if c in df.columns],
        errors="ignore"
    )
    return df