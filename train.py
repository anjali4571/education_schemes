"""
Train the Random Forest match-score model using education_level and education_stream.
"""
import os,json,joblib,pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error,r2_score,mean_absolute_error
from eligibility_engine import load_schemes
from features import generate_citizens,build_training_pairs,encode_features

def train():
    schemes_path="data/educational_schemes_preprocessed_v2.csv"
    schemes_df=load_schemes(schemes_path)
    states=sorted(schemes_df.loc[schemes_df["level"]=="State","state"].dropna().unique().tolist())
    citizens_df=generate_citizens(n=500,states=states,seed=42)
    pairs_df=build_training_pairs(citizens_df,schemes_df)
    eligible_pairs=pairs_df[pairs_df["eligible"]==1].copy()
    print(f"Total pairs: {len(pairs_df)} | Eligible: {len(eligible_pairs)}")
    if len(eligible_pairs)<20: raise RuntimeError("Too few eligible training pairs.")
    encoded=encode_features(eligible_pairs)
    y=encoded["match_score"]
    X=encoded.drop(columns=["eligible","match_score"],errors="ignore")
    X_train,X_test,y_train,y_test=train_test_split(X,y,test_size=.2,random_state=42)
    model=RandomForestRegressor(n_estimators=150,max_depth=14,random_state=42,n_jobs=-1)
    model.fit(X_train,y_train)
    pred=model.predict(X_test)
    metrics={"RandomForestRegressor":{"MAE":round(mean_absolute_error(y_test,pred),4),
                                     "MSE":round(mean_squared_error(y_test,pred),4),
                                     "R2 Score":round(r2_score(y_test,pred),4)}}
    os.makedirs("models",exist_ok=True)
    joblib.dump({"model":model,"columns":list(X.columns)},"models/match_score_regressor.joblib")
    with open("models/metrics.json","w") as f: json.dump(metrics,f,indent=4)
    print(metrics)
if __name__=="__main__": train()
