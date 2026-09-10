"""
Recommendation engine: Hard filtering -> Match Scoring -> Explanation generation.
"""

import os
import joblib
import pandas as pd

from eligibility_engine import load_schemes, filter_eligible_schemes, matches
from features import encode_features


def _score_row(citizen, scheme):
    return {
        "age": citizen["age"],
        "gender": citizen["gender"],
        "caste_category": citizen["caste_category"],
        "income": citizen["income"],
        "state": citizen["state"],
        "education_level": citizen["education_level"],
        "course": citizen["course"],
        "marks_percentage": citizen["marks_percentage"],
        "institution_type": citizen["institution_type"],
        "scheme_id": scheme["scheme_id"],
        "scheme_gender": scheme["gender"],
        "scheme_caste": scheme["caste_category"],
        "scheme_min_age": scheme["min_age"],
        "scheme_max_age": scheme["max_age"],
        "scheme_max_income": scheme["max_income"],
        "scheme_education_level": scheme["education_level"],
        "scheme_course": scheme["course"],
        "scheme_min_marks": scheme["min_marks"],
        "scheme_institution_type": scheme["institution_type"],
        "scheme_level": scheme["level"],
    }


def explain(citizen, scheme):
    reasons = []

    if scheme["level"] == "State":
        reasons.append(f"resident of {scheme['state']}")
    else:
        reasons.append("Central / All-India scheme")

    if scheme["gender"] != "All":
        reasons.append(f"{scheme['gender'].lower()} applicant")
    if scheme["caste_category"] != "All":
        reasons.append(f"{scheme['caste_category']} category")
    if scheme["max_income"] != -1:
        reasons.append(f"family income within Rs {int(scheme['max_income']):,} limit")
    if scheme["education_level"] != "All":
        reasons.append(f"for {scheme['education_level']} students")
    if scheme["course"] not in ["All", "All/General", "General/Any"]:
        reasons.append(f"matches course: {scheme['course']}")
    if scheme["min_marks"] > 0:
        reasons.append(
            f"meets minimum marks requirement of {int(scheme['min_marks'])}%"
        )
    else:
        reasons.append("no documented minimum marks requirement")
    if scheme["institution_type"] != "All":
        reasons.append(f"{scheme['institution_type']} institution")

    reasons.append(
        f"age {citizen['age']} within "
        f"{int(scheme['min_age'])}-{int(scheme['max_age'])} band"
    )
    return "Matched because: " + "; ".join(reasons) + "."


def recommend(
    citizen: dict,
    schemes_path="data/educational_schemes_min_marks_cleaned.csv",
    reg_path="models/match_score_regressor.joblib",
    top_n=10,
):
    schemes = load_schemes(schemes_path)
    eligible = filter_eligible_schemes(citizen, schemes)

    if eligible.empty:
        return eligible.assign(match_score=pd.Series(dtype=float))

    if not os.path.exists(reg_path):
        eligible = eligible.copy()
        def fallback_score(row):
            score = 50.0
            if matches(row["education_level"], citizen["education_level"]):
                score += 10
            if matches(row["course"], citizen["course"]):
                score += 10
            if matches(row["institution_type"], citizen["institution_type"]):
                score += 5
            if matches(row["caste_category"], citizen["caste_category"]):
                score += 10
            if matches(row["gender"], citizen["gender"]):
                score += 5
            if row["min_marks"] > 0:
                score += min(
                    10, max(0, citizen["marks_percentage"] - row["min_marks"]) / 2
                )
            return min(100, score)
        eligible["match_score"] = eligible.apply(fallback_score, axis=1)
        eligible["why_recommended"] = [
            explain(citizen, s) for _, s in eligible.iterrows()
        ]
        return eligible.sort_values("match_score", ascending=False).head(top_n).reset_index(drop=True)

    bundle = joblib.load(reg_path)
    reg_model, columns = bundle["model"], bundle["columns"]

    rows = [_score_row(citizen, s) for _, s in eligible.iterrows()]
    pairs_df = pd.DataFrame(rows)
    encoded = encode_features(pairs_df.assign(eligible=1, match_score=0))
    encoded = encoded.drop(columns=["eligible", "match_score"], errors="ignore")

    for col in columns:
        if col not in encoded.columns:
            encoded[col] = 0
    encoded = encoded[columns]

    scores = reg_model.predict(encoded)

    eligible = eligible.copy()
    eligible["match_score"] = (scores * 100).clip(0, 100).round(1)
    eligible["why_recommended"] = [
        explain(citizen, s) for _, s in eligible.iterrows()
    ]

    return eligible.sort_values(
        "match_score", ascending=False
    ).head(top_n).reset_index(drop=True)