"""
Free-text student profile parser.
"""
import re
GENDER_KEYWORDS={"woman":"Female","women":"Female","female":"Female","girl":"Female","man":"Male","men":"Male","male":"Male","boy":"Male","transgender":"Transgender","trans":"Transgender"}
CASTE_KEYWORDS=["SC","ST","OBC","General","Minority"]
EDUCATION_LEVEL_KEYWORDS={
"10th":"School","class 10":"School","class x":"School","school":"School",
"12th":"Senior Secondary","class 12":"Senior Secondary","class xii":"Senior Secondary","intermediate":"Senior Secondary","senior secondary":"Senior Secondary",
"diploma":"Diploma","iti":"Diploma","polytechnic":"Diploma",
"undergraduate":"Undergraduate","under graduate":"Undergraduate","undergrad":"Undergraduate","ug":"Undergraduate","bachelor":"Undergraduate","btech":"Undergraduate","b.tech":"Undergraduate","b.e":"Undergraduate","bsc":"Undergraduate","b.sc":"Undergraduate","ba":"Undergraduate","b.a":"Undergraduate","bcom":"Undergraduate","b.com":"Undergraduate",
"postgraduate":"Postgraduate","post graduate":"Postgraduate","pg":"Postgraduate","masters":"Postgraduate","mtech":"Postgraduate","m.tech":"Postgraduate","msc":"Postgraduate","m.sc":"Postgraduate","ma":"Postgraduate","m.a":"Postgraduate","mba":"Postgraduate",
"phd":"PhD","ph.d":"PhD","doctoral":"PhD","research scholar":"PhD"}
EDUCATION_STREAM_KEYWORDS={
"engineering":"Engineering & Technology","technology":"Engineering & Technology","computer science":"Engineering & Technology","technical":"Engineering & Technology",
"medical":"Medical & Health","medicine":"Medical & Health","nursing":"Medical & Health","pharmacy":"Medical & Health",
"science":"Science","physics":"Science","chemistry":"Science","biology":"Science",
"commerce":"Commerce & Management","management":"Commerce & Management","business":"Commerce & Management",
"arts":"Arts & Humanities","humanities":"Arts & Humanities","law":"Law","agriculture":"Agriculture","education":"Education"}
INDIAN_STATES=["Andhra Pradesh","Arunachal Pradesh","Assam","Bihar","Chhattisgarh","Goa","Gujarat","Haryana","Himachal Pradesh","Jharkhand","Karnataka","Kerala","Maharashtra","Madhya Pradesh","Manipur","Meghalaya","Mizoram","Nagaland","Odisha","Punjab","Rajasthan","Sikkim","Tamil Nadu","Telangana","Tripura","Uttar Pradesh","Uttarakhand","West Bengal","Delhi","Jammu and Kashmir","Ladakh","Puducherry","Chandigarh","Andaman and Nicobar Islands","Lakshadweep","Dadra and Nagar Haveli and Daman and Diu"]
def _parse_income(text):
    t=text.lower()
    m=re.search(r"(\d+(?:\.\d+)?)\s*lakh",t)
    if m:return int(float(m.group(1))*100000)
    m=re.search(r"(\d+(?:\.\d+)?)\s*crore",t)
    if m:return int(float(m.group(1))*10000000)
    m=re.search(r"income[^\d]{0,15}(\d{4,9})",t)
    if m:return int(m.group(1))
    m=re.search(r"(\d{5,9})\s*(?:rs|rupees|inr)?\s*(?:per year|/year|annually)?",t)
    return int(m.group(1)) if m else None
def _parse_age(text):
    for p in [r"(\d{1,3})\s*(?:years?|yrs?)[\s-]*old",r"\bage\s*[:\-]?\s*(\d{1,3})\b",r"\b(\d{1,2})\s*year old\b"]:
        m=re.search(p,text,re.I)
        if m:return int(m.group(1))
    return None
def _parse_gender(text):
    for kw,val in GENDER_KEYWORDS.items():
        if re.search(rf"\b{re.escape(kw)}\b",text.lower()): return val
    return None
def _parse_caste(text):
    for c in CASTE_KEYWORDS:
        if re.search(rf"\b{re.escape(c)}\b",text,re.I): return c
    return None
def _parse_education_level(text):
    t=text.lower()
    for kw,val in sorted(EDUCATION_LEVEL_KEYWORDS.items(),key=lambda x:-len(x[0])):
        if re.search(rf"(?<!\\w){re.escape(kw)}(?!\\w)", t):
            return val
    return None
def _parse_education_stream(text):
    t=text.lower()
    for kw,val in sorted(EDUCATION_STREAM_KEYWORDS.items(),key=lambda x:-len(x[0])):
        if re.search(rf"(?<!\\w){re.escape(kw)}(?!\\w)", t):
            return val
    return None
def _parse_marks(text):
    t=text.lower()
    for p in [r"(\d{1,3}(?:\.\d+)?)\s*%",r"marks?[^\d]{0,15}(\d{1,3}(?:\.\d+)?)",r"(\d{1,3}(?:\.\d+)?)\s*percent"]:
        m=re.search(p,t)
        if m:
            v=float(m.group(1))
            return v if 0<=v<=100 else None
    return None
def _parse_state(text):
    for state in INDIAN_STATES:
        if re.search(rf"\b{re.escape(state)}\b",text,re.I): return state
    return None
def parse_profile(text):
    return {"age":_parse_age(text),"gender":_parse_gender(text),"caste_category":_parse_caste(text),
            "income":_parse_income(text),"state":_parse_state(text),"education_level":_parse_education_level(text),
            "education_stream":_parse_education_stream(text),"marks_percentage":_parse_marks(text)}
