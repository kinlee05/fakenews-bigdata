import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import joblib

print("Đọc data...")
df = pd.read_csv("../tv1_data_engineer/final_data.csv")
df = df.dropna(subset=["content", "label"])

X = df["content"]
y = df["label"]

print(f"Tổng: {len(df)} dòng")

print("Train model...")
pipeline = Pipeline([
    ("tfidf", TfidfVectorizer(max_features=10000, stop_words="english")),
    ("clf", LogisticRegression(max_iter=100))
])

pipeline.fit(X, y)

joblib.dump(pipeline, "model.pkl")
print("Đã lưu model.pkl ✅")
