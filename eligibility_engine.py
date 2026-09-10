"""
Rule-based eligibility engine for educational schemes.
The current dataset uses education_level + education_stream and does not use
course or institution_type.
"""
import pandas as pd

DATASET_PATH = "data/educational_schemes_preprocessed_v2.csv"

EDU_LEVEL_MAP = {
    "1st-8th": "School",
    "9th-10th": "School",
    "10th": "School",
    "11th-12th": "Senior Secondary",
    "12th": "Senior Secondary",
    "higher secondary": "Senior Secondary",
    "secondary": "School",
    "post-matric": "Senior Secondary",
    "diploma/iti": "Diploma",
    "ug": "Undergraduate",
    "pg": "Postgraduate",
    "phd": "PhD",
    "general": "All",
    "all": "All",
}
STREAM_MAP = {
    "general": "All",
    "all": "All",
    "engineering": "Engineering & Technology",
    "technology": "Engineering & Technology",
    "computer science": "Engineering & Technology",
    "technical": "Engineering & Technology",
    "medical": "Medical & Health",
    "medicine": "Medical & Health",
    "nursing": "Medical & Health",
    "pharmacy": "Medical & Health",
    "science": "Science",
    "physics": "Science",
    "chemistry": "Science",
    "biology": "Science",
    "commerce": "Commerce & Management",
    "management": "Commerce & Management",
    "business": "Commerce & Management",
    "arts": "Arts & Humanities",
    "humanities": "Arts & Humanities",
    "law": "Law",
    "agriculture": "Agriculture",
    "education": "Education",
}

def load_schemes(path=DATASET_PATH):
    df = pd.read_csv(path)
    for col in ["education_level", "education_stream", "gender", "caste_category"]:
        if col in df.columns:
            df[col] = df[col].fillna("All").astype(str).str.strip()
            df[col] = df[col].replace(["", "Not Specified", "N/A", "NA", "General"], "All")
    df["education_level"] = df["education_level"].apply(
        lambda x: EDU_LEVEL_MAP.get(str(x).strip().lower(), x)
    )
    df["education_stream"] = df["education_stream"].apply(
        lambda x: STREAM_MAP.get(str(x).strip().lower(), x)
    )
    df["min_marks"] = pd.to_numeric(df["min_marks"], errors="coerce").fillna(0).clip(0,100)
    df["max_income"] = pd.to_numeric(df["max_income"], errors="coerce").fillna(-1)
    df.loc[df["max_income"] < 0, "max_income"] = -1
    df["min_age"] = pd.to_numeric(df["min_age"], errors="coerce").fillna(5).clip(0,100)
    df["max_age"] = pd.to_numeric(df["max_age"], errors="coerce").fillna(99).clip(0,120)
    swap = df["min_age"] > df["max_age"]
    if swap.any():
        df.loc[swap, ["min_age","max_age"]] = df.loc[swap, ["max_age","min_age"]].to_numpy()
    if "official_link" in df.columns:
        df = df.drop(columns=["official_link"])
    if "course" in df.columns:
        df = df.drop(columns=["course"])
    if "institution_type" in df.columns:
        df = df.drop(columns=["institution_type"])
    return df

def _norm(value):
    return str(value).strip().lower()

def matches(scheme_value, student_value):
    scheme_str, student_str = _norm(scheme_value), _norm(student_value)
    if scheme_str in {"all", "all india", "general/any", "all/general"}:
        return True
    scheme_edu = EDU_LEVEL_MAP.get(scheme_str, scheme_str)
    student_edu = EDU_LEVEL_MAP.get(student_str, student_str)
    if scheme_edu == "all" or scheme_edu == student_edu:
        return True
    scheme_stream = STREAM_MAP.get(scheme_str, scheme_str)
    student_stream = STREAM_MAP.get(student_str, student_str)
    if scheme_stream == "all" or scheme_stream == student_stream:
        return True
    return student_str in scheme_str or scheme_str in student_str

def is_eligible(citizen, scheme):
    if scheme["level"] == "State" and _norm(scheme["state"]) != _norm(citizen["state"]):
        return False
    if not matches(scheme["gender"], citizen["gender"]): return False
    if not matches(scheme["caste_category"], citizen["caste_category"]): return False
    if not (scheme["min_age"] <= citizen["age"] <= scheme["max_age"]): return False
    if scheme["max_income"] != -1 and citizen["income"] > scheme["max_income"]: return False
    if not matches(scheme["education_level"], citizen["education_level"]): return False
    if not matches(scheme["education_stream"], citizen["education_stream"]): return False
    if scheme["min_marks"] > 0 and citizen["marks_percentage"] < scheme["min_marks"]: return False
    return True

def filter_eligible_schemes(citizen, df):
    mask = df.apply(lambda row: is_eligible(citizen, row), axis=1)
    return df[mask].copy()

if __name__ == "__main__":
    df=load_schemes()
    sample={"age":19,"gender":"Female","caste_category":"SC","income":150000,
            "state":"Maharashtra","education_level":"Undergraduate",
            "education_stream":"Engineering & Technology","marks_percentage":78}
    print("Matched eligible schemes:",len(filter_eligible_schemes(sample,df)))
