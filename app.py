"""
app.py
Streamlit UI for the AI Educational Schemes Recommendation System.
Tabs: Profile Form | Analytics Dashboard
Styled with custom CSS: gradient hero header, animated fade-in scheme
cards, animated match-score bars, hover effects, and styled tabs.
"""
import json
import time
import pandas as pd
import streamlit as st

from eligibility_engine import load_schemes
from recommender import recommend

st.set_page_config(page_title="AI Educational Scheme Recommender", page_icon="🎓", layout="wide")

INDIAN_STATES = ["Andhra Pradesh","Arunachal Pradesh","Assam","Bihar","Chhattisgarh","Goa","Gujarat","Haryana","Himachal Pradesh","Jharkhand","Karnataka","Kerala","Maharashtra","Madhya Pradesh","Manipur","Meghalaya","Mizoram","Nagaland","Odisha","Punjab","Rajasthan","Sikkim","Tamil Nadu","Telangana","Tripura","Uttar Pradesh","Uttarakhand","West Bengal","Delhi","Jammu and Kashmir","Ladakh","Puducherry","Chandigarh","Andaman and Nicobar Islands","Lakshadweep","Dadra and Nagar Haveli and Daman and Diu"]

CASTE_OPTIONS = ["General", "OBC", "SC", "ST", "Minority"]
GENDER_OPTIONS = ["Male", "Female", "Transgender"]
EDUCATION_LEVEL_OPTIONS = ["School", "Senior Secondary", "Diploma",
                           "Undergraduate", "Postgraduate", "PhD"]
EDUCATION_STREAM_OPTIONS = [
    "General", "Engineering & Technology", "Medical & Health", "Science",
    "Commerce & Management", "Arts & Humanities", "Law", "Agriculture", "Education"
]

# ------------------------------------------------------------------
# CUSTOM CSS  (gradients, fade/slide-in animations, hover effects,
# animated progress bars, styled tabs & metric cards)
# ------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');

html, body, [class*="css"]  { font-family: 'Poppins', sans-serif; }

body {
    background-color: #eee8f8 !important;
}

.stApp {
    background-color: #eee8f8 !important;
}

/* ---------- Soft page background ---------- */
.stApp {
    background: #f7f5fb;
}

/* ---------- Animations ---------- */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(18px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes fadeIn {
    from { opacity: 0; }
    to   { opacity: 1; }
}
@keyframes gradientShift {
    0%   { background-position: 0% 50%; }
    50%  { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
@keyframes fillBar {
    from { width: 0%; }
}
@keyframes floatIcon {
    0%, 100% { transform: translateY(0px); }
    50%      { transform: translateY(-6px); }
}
@keyframes pulseGlow {
    0%, 100% { box-shadow: 0 0 0 0 rgba(102, 126, 234, 0.35); }
    50%      { box-shadow: 0 0 0 10px rgba(102, 126, 234, 0); }
}

/* ---------- Hero header ---------- */
.hero {
    background: linear-gradient(120deg, #667eea, #764ba2, #6a82fb, #764ba2);
    background-size: 300% 300%;
    border-radius: 18px;
    padding: 2.1rem 2rem;
    margin-bottom: 1.6rem;
    text-align: center;
    box-shadow: 0 10px 30px rgba(102, 92, 246, 0.25);
    animation: gradientShift 10s ease infinite, fadeIn 0.8s ease;
}
.hero .icon {
    font-size: 2.6rem;
    display: inline-block;
    animation: floatIcon 3s ease-in-out infinite;
}
.hero h1 {
    color: white;
    font-weight: 700;
    font-size: 2.1rem;
    margin: 0.3rem 0 0.2rem 0;
    letter-spacing: 0.3px;
}
.hero p {
    color: rgba(255,255,255,0.9);
    font-size: 1.02rem;
    margin: 0;
}

/* ---------- Tabs ---------- */
button[data-baseweb="tab"] {
    font-weight: 600;
    font-size: 1.02rem;
    padding: 10px 18px !important;
    border-radius: 10px 10px 0 0 !important;
    transition: all 0.25s ease;
}
button[data-baseweb="tab"]:hover {
    background: rgba(102, 126, 234, 0.08);
    transform: translateY(-2px);
}
div[data-baseweb="tab-highlight"] {
    background: linear-gradient(90deg, #667eea, #764ba2) !important;
    height: 3px !important;
}

/* ---------- Scheme result cards ---------- */
.scheme-card {
    background: white;
    border: 1px solid #eef0f7;
    border-radius: 16px;
    padding: 1.3rem 1.5rem;
    margin-bottom: 1.1rem;
    box-shadow: 0 3px 14px rgba(30, 30, 60, 0.06);
    animation: fadeInUp 0.55s ease both;
    transition: transform 0.25s ease, box-shadow 0.25s ease;
    position: relative;
    overflow: hidden;
}
.scheme-card:hover {
    transform: translateY(-4px) scale(1.005);
    box-shadow: 0 12px 28px rgba(102, 126, 234, 0.18);
    border-color: #c9d1f7;
}
.scheme-card::before {
    content: "";
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 5px;
    background: linear-gradient(180deg, #667eea, #764ba2);
}
.scheme-title {
    font-size: 1.15rem;
    font-weight: 700;
    color: #262730;
    margin: 0 0 2px 0;
}
.scheme-meta {
    font-size: 0.82rem;
    color: #8a8fa3;
    margin-bottom: 0.55rem;
    font-weight: 500;
}
.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 600;
    margin-right: 6px;
}
.badge-central { background: #e8f0fe; color: #1a56db; }
.badge-state   { background: #eafaf0; color: #027a48; }

.benefit-line {
    background: #f6f7fb;
    border-radius: 10px;
    padding: 8px 12px;
    font-size: 0.92rem;
    margin: 0.5rem 0;
    border-left: 3px solid #764ba2;
}
.why-box {
    background: linear-gradient(90deg, #fff8e6, #fffdf5);
    border: 1px solid #ffe8a3;
    border-radius: 10px;
    padding: 8px 12px;
    font-size: 0.86rem;
    color: #6b5900;
    margin-top: 0.5rem;
}

/* ---------- Match score ring/bar ---------- */
.score-wrap { text-align: center; }
.score-num {
    font-size: 1.6rem;
    font-weight: 700;
    background: linear-gradient(90deg, #667eea, #764ba2);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: pulseGlow 2.4s ease-in-out infinite;
    border-radius: 50%;
    padding: 6px;
}
.score-bar-bg {
    width: 100%;
    background: #eef0f7;
    border-radius: 8px;
    height: 8px;
    margin-top: 6px;
    overflow: hidden;
}
.score-bar-fill {
    height: 8px;
    border-radius: 8px;
    background: linear-gradient(90deg, #667eea, #764ba2);
    animation: fillBar 1.1s ease-out both;
}

/* ---------- KPI metric cards (Analytics tab) ---------- */
.kpi-card {
    background: linear-gradient(135deg, #ffffff, #f5f6fd);
    border-radius: 14px;
    padding: 1rem 1rem 0.8rem 1rem;
    text-align: center;
    box-shadow: 0 3px 12px rgba(30,30,60,0.06);
    animation: fadeInUp 0.5s ease both;
    border: 1px solid #eef0f7;
    transition: transform 0.2s ease;
}
.kpi-card:hover { transform: translateY(-3px); }
.kpi-num {
    font-size: 1.7rem;
    font-weight: 700;
    background: linear-gradient(90deg, #667eea, #764ba2);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.kpi-label { font-size: 0.82rem; color: #8a8fa3; font-weight: 500; margin-top: 2px; }

/* ---------- Buttons ---------- */
div.stButton > button {
    background: linear-gradient(90deg, #667eea, #764ba2);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 0.55rem 1.4rem;
    font-weight: 600;
    transition: all 0.25s ease;
    box-shadow: 0 4px 14px rgba(102, 126, 234, 0.3);
}
div.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 22px rgba(102, 126, 234, 0.42);
    filter: brightness(1.05);
}
div.stButton > button:active { transform: translateY(0px); }

/* ---------- Fade the whole results block in ---------- */
.results-wrap { animation: fadeIn 0.4s ease; }

</style>
""", unsafe_allow_html=True)


@st.cache_data
def get_schemes():
    return load_schemes("data/educational_schemes_preprocessed_v2.csv")


def render_results(results: pd.DataFrame):
    if results.empty:
        st.warning("😕 No matching scholarships/schemes found for this profile. Try adjusting the details.")
        return
    st.markdown(f"""
    <div style="animation:fadeIn 0.5s ease; margin-bottom:0.8rem;">
        <span style="background:#eafaf0;color:#027a48;padding:6px 14px;border-radius:20px;
        font-weight:600;font-size:0.92rem;">
        ✅ Found {len(results)} matching educational schemes, ranked by relevance
        </span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="results-wrap">', unsafe_allow_html=True)
    for i, (_, r) in enumerate(results.iterrows()):
        delay = min(i * 0.06, 0.5)
        level_badge = ('<span class="badge badge-central">🇮🇳 Central</span>'
                        if r["level"] == "Central"
                        else '<span class="badge badge-state">📍 State</span>')
        score = float(r["match_score"])
        st.markdown(f"""
        <div class="scheme-card" style="animation-delay:{delay}s;">
            <div style="display:flex; justify-content:space-between; gap:1rem; align-items:flex-start;">
                <div style="flex:1;">
                    <div class="scheme-title">{r['scheme_name']}</div>
                    <div class="scheme-meta">{level_badge} {r['state']} · {r['department']}</div>
                    <div>{r['description']}</div>
                    <div class="benefit-line">💰 <b>Benefits:</b> {r['benefits']}</div>
                    <div class="why-box">🔎 {r['why_recommended']}</div>
                </div>
                <div class="score-wrap" style="min-width:90px;">
                    <div class="score-num">{score:.0f}%</div>
                    <div class="score-bar-bg">
                        <div class="score-bar-fill" style="width:{score}%;"></div>
                    </div>
                    <div style="font-size:0.7rem;color:#8a8fa3;margin-top:3px;">MATCH</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


def profile_to_citizen(age, gender, caste, income, state, education_level,
                        education_stream, marks_percentage):
    return {"age": age, "gender": gender, "caste_category": caste,
            "income": income, "state": state,
            "education_level": education_level,
            "education_stream": education_stream,
            "marks_percentage": marks_percentage}


def kpi_card(number, label):
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-num">{number}</div>
        <div class="kpi-label">{label}</div>
    </div>
    """, unsafe_allow_html=True)


# ------------------------------------------------------------------
# HERO HEADER
# ------------------------------------------------------------------
st.markdown("""
<div class="hero">
    <div class="icon">🎓</div>
    <h1>AI Educational Schemes Recommendation System</h1>
    <p>Find scholarships & educational schemes you're eligible for — ranked by a machine-learned match score</p>
</div>
""", unsafe_allow_html=True)

tab1, tab3 = st.tabs(["📝  Profile Form", "📊  Analytics Dashboard"])

# ------------------------------------------------------------------
# TAB 1: Profile Form
# ------------------------------------------------------------------
with tab1:
    st.subheader("Enter your details")

    # All profile inputs are dropdown/select controls — no text inputs.
    age_options = list(range(5, 36))
    income_options = [
        0, 25000, 50000, 75000, 100000, 125000, 150000, 200000,
        250000, 300000, 400000, 500000, 600000, 800000, 1000000,
        1200000, 1500000, 2000000, 3000000, 5000000, 10000000
    ]
    marks_options = [float(x) for x in range(0, 101)]

    col1, col2, col3 = st.columns(3)
    with col1:
        age = st.selectbox("Age", age_options, index=14)
        gender = st.selectbox("Gender", GENDER_OPTIONS)
    with col2:
        caste = st.selectbox("Caste Category", CASTE_OPTIONS)
        education_level = st.selectbox("Education Level", EDUCATION_LEVEL_OPTIONS)
    with col3:
        income = st.selectbox(
            "Annual Family Income (Rs)",
            income_options,
            index=6,
            format_func=lambda x: f"₹{x:,}"
        )
        state_options = sorted(set(INDIAN_STATES) | {"Maharashtra"})
        state = st.selectbox("State / UT", state_options)

    col4, col5, col6 = st.columns(3)
    with col4:
        education_stream = st.selectbox("Education Stream", EDUCATION_STREAM_OPTIONS)
    with col5:
        marks_percentage = st.selectbox(
            "Marks / Percentage (%)",
            marks_options,
            index=75,
            format_func=lambda x: f"{x:g}%"
        )
    with col6:
        st.empty()

    if st.button("🔍  Find Eligible Schemes", type="primary", key="form_search"):
        citizen = profile_to_citizen(
            age, gender, caste, income, state,
            education_level, education_stream, marks_percentage
        )
        with st.spinner("Matching your profile against eligibility rules and ML rankings..."):
            time.sleep(0.4)
            results = recommend(
                citizen,
                schemes_path="data/educational_schemes_preprocessed_v2.csv",
                top_n=15
            )
        render_results(results)

# ------------------------------------------------------------------
# TAB 3: Analytics Dashboard
# ------------------------------------------------------------------
with tab3:
    st.subheader("Dataset Analytics")
    schemes = get_schemes()

    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi_card(len(schemes), "Total Schemes")
    with c2: kpi_card(schemes.loc[schemes.level == "State", "state"].nunique(), "States/UTs Covered")
    with c3: kpi_card((schemes.level == "Central").sum(), "Central Schemes")
    with c4: kpi_card(schemes["category"].nunique(), "Categories")

    st.markdown("<br>", unsafe_allow_html=True)

    colA, colB = st.columns(2)
    with colA:
        st.markdown("**📍 Schemes by State**")
        state_counts = schemes.loc[schemes.level == "State", "state"].value_counts()
        st.bar_chart(state_counts, color="#764ba2")
    with colB:
        st.markdown("**🗂️ Schemes by Category**")
        st.bar_chart(schemes["category"].value_counts(), color="#667eea")

    colC, colD = st.columns(2)
    with colC:
        st.markdown("**🎓 Schemes by Education Level**")
        st.bar_chart(schemes["education_level"].value_counts(), color="#f6a5c0")
    with colD:
        st.markdown("**📚 Schemes by Education Stream**")
        st.bar_chart(schemes["education_stream"].value_counts(), color="#6a82fb")

    colE, colF = st.columns(2)
    with colE:
        st.markdown("**🚻 Schemes by Gender Eligibility**")
        st.bar_chart(schemes["gender"].value_counts(), color="#8fd3c7")
    with colF:
        st.markdown("**🏷️ Schemes by Caste Category**")
        st.bar_chart(schemes["caste_category"].value_counts(), color="#ffb894")

    st.markdown("**🧠 Model Performance (from training)**")
    try:
        with open("models/metrics.json") as f:
            metrics = json.load(f)
        st.dataframe(pd.DataFrame(metrics).T, use_container_width=True)
    except FileNotFoundError:
        st.info("Run `python train_model.py` to generate model performance metrics.")

    with st.expander("📄 View full scheme dataset"):
        st.dataframe(schemes, use_container_width=True)
