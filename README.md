# AI Educational Schemes Recommendation System

## Dataset
Main dataset:
`data/educational_schemes_min_marks_cleaned.csv`

The application does not use an `official_link` column.

### Important data convention
- `min_marks = 0` means **no documented minimum marks requirement**.
- `max_income = -1` means **no income limit**.

## Run
```bash
pip install streamlit pandas numpy scikit-learn joblib
streamlit run app.py
```

## Model training
If you have a `train_model.py`, update it to use:
`data/educational_schemes_min_marks_cleaned.csv`

`features.py` can generate:
`data/training_pairs.csv`

The application can also run without a trained regressor; it uses a fallback relevance score until the ML model is trained.

## Profile Form
The Profile Form uses dropdown/select controls instead of text input for:
- Age
- Gender
- Caste
- Education Level
- Annual Income
- State
- Course
- Marks
- Institution Type

The chatbot tab remains free-text because it is specifically the natural-language profile parser.
