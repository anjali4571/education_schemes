# AI Educational Schemes Recommendation System

## Updated dataset
The project uses:
`data/educational_schemes_preprocessed_v2.csv`

The preprocessing standardizes numeric eligibility fields and education labels and removes the obsolete `course` field. The dataset does not contain `institution_type`.

## Prediction features
Both of these are used by the eligibility engine, feature engineering, and ML model:
- `education_level`
- `education_stream`

Other profile features:
- Age
- Gender
- Caste Category
- Annual Family Income
- State
- Marks / Percentage

## Recommendation pipeline
Student Profile -> Rule-based Eligibility -> Eligible Schemes -> Feature Encoding -> Random Forest Regressor -> Match Score -> Top Recommendations

## Run
```bash
pip install streamlit pandas numpy scikit-learn joblib
python train.py
streamlit run app.py
```

Run `python train.py` after changing the dataset so the model is retrained with the current feature set.

## Model files
- `models/match_score_regressor.joblib`
- `models/metrics.json`

## Important data conventions
- `min_marks = 0` means no documented minimum marks requirement.
- `max_income = -1` means no income limit.
- `All` is treated as a wildcard for applicable categorical eligibility fields.
