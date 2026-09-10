"""
Rule-based eligibility engine for educational schemes.
Normalizes dataset values and maps them directly to UI dropdown selections.
"""

import pandas as pd

DATASET_PATH = "data/educational_schemes_min_marks_cleaned.csv"

# Category normalization dictionaries
EDU_LEVEL_MAP = {
    "1st-8th": "School",
    "9th-10th": "School",
    "11th-12th": "Senior Secondary",
    "post-matric": "Senior Secondary",
    "diploma/iti": "Diploma",
    "ug": "Undergraduate",
    "pg": "Postgraduate",
    "phd": "PhD",
    "all": "All",
}

INSTITUTION_MAP = {
    "government/approved institution": "Government",
    "private institution": "Private",
    "institution not specified": "All",
    "all": "All",
}


def load_schemes(path=DATASET_PATH):
    df = pd.read_csv(path)

    # Defensive fill for empty or blank values
    for col in ["education_level", "course", "institution_type", "gender", "caste_category"]:
        if col in df.columns:
            df[col] = df[col].fillna("All").replace(["", "Not Specified", "N/A", "NA"], "All")

    # Numeric standardization
    df["min_marks"] = pd.to_numeric(df["min_marks"], errors="coerce").fillna(0)
    df.loc[df["min_marks"] < 0, "min_marks"] = 0

    df["max_income"] = pd.to_numeric(df["max_income"], errors="coerce").fillna(-1)
    df.loc[df["max_income"] < 0, "max_income"] = -1

    df["min_age"] = pd.to_numeric(df["min_age"], errors="coerce").fillna(5)
    df["max_age"] = pd.to_numeric(df["max_age"], errors="coerce").fillna(99)

    if "official_link" in df.columns:
        df = df.drop(columns=["official_link"])

    return df


def matches(scheme_value, student_value):
    """
    Normalizes exact values across the dataset and compares against UI input choices.
    """
    scheme_str = str(scheme_value).strip().lower()
    student_str = str(student_value).strip().lower()

    # Wildcards / Open eligibility
    if scheme_str in {"all", "all india", "general/any", "institution not specified", "all/general"}:
        return True

    # Exact normalized match for Education Level
    scheme_edu = EDU_LEVEL_MAP.get(scheme_str, scheme_str)
    student_edu = EDU_LEVEL_MAP.get(student_str, student_str)
    if scheme_edu == student_edu or scheme_edu == "all":
        return True

    # Exact normalized match for Institution Type
    scheme_inst = INSTITUTION_MAP.get(scheme_str, scheme_str)
    student_inst = INSTITUTION_MAP.get(student_str, student_str)
    if scheme_inst == student_inst or scheme_inst == "all":
        return True

    # Token/Substring match for multi-value categories (e.g., Caste: "SC/ST", Course: "Engineering/Technology")
    return student_str in scheme_str or scheme_str in student_str


def is_eligible(citizen: dict, scheme: pd.Series) -> bool:
    if scheme["level"] == "State":
        if str(scheme["state"]).strip().lower() != str(citizen["state"]).strip().lower():
            return False

    if not matches(scheme["gender"], citizen["gender"]):
        return False

    if not matches(scheme["caste_category"], citizen["caste_category"]):
        return False

    if not (scheme["min_age"] <= citizen["age"] <= scheme["max_age"]):
        return False

    if scheme["max_income"] != -1 and citizen["income"] > scheme["max_income"]:
        return False

    if not matches(scheme["education_level"], citizen["education_level"]):
        return False

    if not matches(scheme["course"], citizen["course"]):
        return False

    if scheme["min_marks"] > 0 and citizen["marks_percentage"] < scheme["min_marks"]:
        return False

    if not matches(scheme["institution_type"], citizen["institution_type"]):
        return False

    return True


def filter_eligible_schemes(citizen: dict, df: pd.DataFrame) -> pd.DataFrame:
    mask = df.apply(lambda row: is_eligible(citizen, row), axis=1)
    return df[mask].copy()


if __name__ == "__main__":
    df = load_schemes()
    sample_citizen = {
        "age": 19,
        "gender": "Female",
        "caste_category": "SC",
        "income": 150000,
        "state": "Maharashtra",
        "education_level": "Undergraduate",
        "course": "Engineering",
        "marks_percentage": 78,
        "institution_type": "Government",
    }
    result = filter_eligible_schemes(sample_citizen, df)
    print(f"Matched eligible schemes: {len(result)}")