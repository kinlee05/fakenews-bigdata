from fastapi import FastAPI
from pydantic import BaseModel

from pyspark.sql import SparkSession
from pyspark.ml import PipelineModel

app = FastAPI()

# Khởi tạo Spark
spark = SparkSession.builder \
    .appName("FakeNewsAPI") \
    .master("local[*]") \
    .getOrCreate()

# Load model của TV3
model = PipelineModel.load(
    "../tv3_ml/saved_model/logistic_regression"
)

class InputText(BaseModel):
    text: str

@app.post("/predict")
def predict(data: InputText):

    df = spark.createDataFrame(
        [(data.text,)],
        ["content"]
    )

    result = model.transform(df)

    row = result.select(
        "prediction",
        "probability"
    ).collect()[0]

    prediction = int(row["prediction"])

    probs = row["probability"]

    confidence = float(probs[prediction])

    return {
        "prediction": prediction,
        "label": "FAKE" if prediction == 1 else "REAL",
        "confidence": confidence
    }

@app.get("/health")
def health():
    return {"status": "ok"}
