from fastapi import FastAPI
from pydantic import BaseModel
import joblib

app = FastAPI()

model = joblib.load("model.pkl")

class InputText(BaseModel):
    text: str

@app.post("/predict")
def predict(data: InputText):
    proba = model.predict_proba([data.text])[0]
    classes = model.classes_
    idx = proba.argmax()
    label = classes[idx]
    confidence = float(proba[idx])
    return {"label": label, "confidence": confidence}

@app.get("/health")
def health():
    return {"status": "ok"}
