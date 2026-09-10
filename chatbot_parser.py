"""
Free-text student profile parser for the educational schemes system.
"""

import re

GENDER_KEYWORDS = {
    "woman": "Female", "women": "Female", "female": "Female", "girl": "Female",
    "man": "Male", "men": "Male", "male": "Male", "boy": "Male",
    "transgender": "Transgender", "trans": "Transgender",
}

CASTE_KEYWORDS = ["SC", "ST", "OBC", "General", "Minority"]

EDUCATION_LEVEL_KEYWORDS = {
    "10th": "School", "class 10": "School", "class x": "School", "school": "School",
    "12th": "Senior Secondary", "class 12": "Senior Secondary",
    "class xii": "Senior Secondary", "intermediate": "Senior Secondary",
    "senior secondary": "Senior Secondary",
    "diploma": "Diploma", "iti": "Diploma", "polytechnic": "Diploma",
    "undergraduate": "Undergraduate", "under graduate": "Undergraduate",
    "ug": "Undergraduate", "bachelor": "Undergraduate", "btech": "Undergraduate",
    "b.tech": "Undergraduate", "b.e": "Undergraduate", "bsc": "Undergraduate",
    "b.sc": "Undergraduate", "ba": "Undergraduate", "b.a": "Undergraduate",
    "bcom": "Undergraduate", "b.com": "Undergraduate",
    "postgraduate": "Postgraduate", "post graduate": "Postgraduate",
    "pg": "Postgraduate", "masters": "Postgraduate", "mtech": "Postgraduate",
    "m.tech": "Postgraduate", "msc": "Postgraduate", "m.sc": "Postgraduate",
    "ma": "Postgraduate", "m.a": "Postgraduate", "mba": "Postgraduate",
    "phd": "PhD", "ph.d": "PhD", "doctoral": "PhD", "research scholar": "PhD",
}

COURSE_KEYWORDS = {
    "engineering": "Engineering", "btech": "Engineering", "b.tech": "Engineering",
    "mtech": "Engineering", "m.tech": "Engineering", "b.e": "Engineering",
    "medical": "Medical", "mbbs": "Medical", "medicine": "Medical", "nursing": "Medical",
    "law": "Law", "llb": "Law", "ll.b": "Law",
    "management": "Management", "mba": "Management", "bba": "Management",
    "commerce": "Commerce", "bcom": "Commerce", "b.com": "Commerce", "mcom": "Commerce",
    "science": "Science", "bsc": "Science", "b.sc": "Science", "msc": "Science", "m.sc": "Science",
    "arts": "Arts", "ba": "Arts", "b.a": "Arts", "ma": "Arts", "m.a": "Arts",
    "vocational": "Vocational/ITI", "iti": "Vocational/ITI", "polytechnic": "Vocational/ITI",
}

INSTITUTION_TYPE_KEYWORDS = {
    "government college": "Government", "govt college": "Government",
    "government school": "Government", "govt school": "Government",
    "government institute": "Government", "govt institute": "Government",
    "private college": "Private", "private school": "Private",
    "private institute": "Private",
    "aided college": "Aided", "aided school": "Aided", "grant-in-aid": "Aided",
}

INDIAN_STATES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
    "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
    "Kerala", "Maharashtra", "Madhya Pradesh", "Manipur", "Meghalaya", "Mizoram", "Nagaland",
    "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana",
    "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal", "Delhi",
    "Jammu and Kashmir", "Ladakh", "Puducherry", "Chandigarh",
    "Andaman and Nicobar Islands", "Lakshadweep",
    "Dadra and Nagar Haveli and Daman and Diu",
]


def _parse_income(text):
    text_l = text.lower()
    m = re.search(r"(\d+(?:\.\d+)?)\s*lakh", text_l)
    if m:
        return int(float(m.group(1)) * 100000)
    m = re.search(r"(\d+(?:\.\d+)?)\s*crore", text_l)
    if m:
        return int(float(m.group(1)) * 10000000)
    m = re.search(r"income[^\d]{0,15}(\d{4,9})", text_l)
    if m:
        return int(m.group(1))
    m = re.search(r"(\d{5,9})\s*(?:rs|rupees|inr)?\s*(?:per year|/year|annually)?", text_l)
    if m:
        return int(m.group(1))
    return None


def _parse_age(text):
    m = re.search(r"(\d{1,3})\s*(?:years?|yrs?)[\s-]*old", text, re.IGNORECASE)
    if m:
        return int(m.group(1))
    m = re.search(r"\bage\s*[:\-]?\s*(\d{1,3})\b", text, re.IGNORECASE)
    if m:
        return int(m.group(1))
    m = re.search(r"\b(\d{1,2})\s*year old\b", text, re.IGNORECASE)
    if m:
        return int(m.group(1))
    return None


def _parse_gender(text):
    text_l = text.lower()
    for kw, val in GENDER_KEYWORDS.items():
        if re.search(rf"\b{re.escape(kw)}\b", text_l):
            return val
    return None


def _parse_caste(text):
    for c in CASTE_KEYWORDS:
        if re.search(rf"\b{re.escape(c)}\b", text, re.IGNORECASE):
            return c
    return None


def _parse_education_level(text):
    text_l = text.lower()
    for kw, val in sorted(EDUCATION_LEVEL_KEYWORDS.items(), key=lambda x: -len(x[0])):
        if kw in text_l:
            return val
    return None


def _parse_course(text):
    text_l = text.lower()
    for kw, val in sorted(COURSE_KEYWORDS.items(), key=lambda x: -len(x[0])):
        if kw in text_l:
            return val
    return None


def _parse_marks(text):
    text_l = text.lower()
    m = re.search(r"(\d{1,3}(?:\.\d+)?)\s*%", text_l)
    if m:
        value = float(m.group(1))
        return value if 0 <= value <= 100 else None
    m = re.search(r"marks?[^\d]{0,15}(\d{1,3}(?:\.\d+)?)", text_l)
    if m:
        value = float(m.group(1))
        return value if 0 <= value <= 100 else None
    m = re.search(r"(\d{1,3}(?:\.\d+)?)\s*percent", text_l)
    if m:
        value = float(m.group(1))
        return value if 0 <= value <= 100 else None
    return None


def _parse_institution_type(text):
    text_l = text.lower()
    for kw, val in sorted(INSTITUTION_TYPE_KEYWORDS.items(), key=lambda x: -len(x[0])):
        if kw in text_l:
            return val
    return None


def _parse_state(text):
    for state in INDIAN_STATES:
        if re.search(rf"\b{re.escape(state)}\b", text, re.IGNORECASE):
            return state
    return None


def parse_profile(text: str) -> dict:
    return {
        "age": _parse_age(text),
        "gender": _parse_gender(text),
        "caste_category": _parse_caste(text),
        "income": _parse_income(text),
        "state": _parse_state(text),
        "education_level": _parse_education_level(text),
        "course": _parse_course(text),
        "marks_percentage": _parse_marks(text),
        "institution_type": _parse_institution_type(text),
    }


if __name__ == "__main__":
    samples = [
        "I am a 19 year old SC girl from Maharashtra, doing engineering undergrad in a government college, 78% marks, family income 1.5 lakh",
        "17 years old, class 12, general category, Punjab, 85 percent marks",
        "My son is 22, ST, doing MBA in a private institute in Odisha, income around 3 lakh",
    ]
    for s in samples:
        print(s)
        print(" ->", parse_profile(s))
