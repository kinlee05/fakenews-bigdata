from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when
from pyspark.ml.feature import Tokenizer, StopWordsRemover, HashingTF, IDF
from pyspark.ml.classification import LogisticRegression, NaiveBayes, RandomForestClassifier
from pyspark.ml import Pipeline
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
import matplotlib.pyplot as plt
import pandas as pd

# ===== 1. KHỞI ĐỘNG SPARK =====
spark = SparkSession.builder \
    .appName("FakeNewsClassification") \
    .master("local[*]") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")
print("✅ Spark khởi động thành công!")

# ===== 2. ĐỌC DỮ LIỆU =====
df = spark.read.csv(
    "../data/raw/final_data.csv",
    header=True,
    inferSchema=True
)

print(f"✅ Đọc dữ liệu xong: {df.count()} dòng")
df.show(3, truncate=50)

# ===== 3. CHUYỂN NHÃN SANG SỐ =====
df = df.withColumn("label_num",
    when(col("label") == "FAKE", 1.0).otherwise(0.0)
)

# ===== 4. CHIA TRAIN/TEST (80/20) =====
train_df, test_df = df.randomSplit([0.8, 0.2], seed=42)
print(f"✅ Train: {train_df.count()} dòng | Test: {test_df.count()} dòng")

# ===== 5. PIPELINE TIỀN XỬ LÝ NLP =====
tokenizer = Tokenizer(inputCol="content", outputCol="words")
remover = StopWordsRemover(inputCol="words", outputCol="filtered")
hashingTF = HashingTF(inputCol="filtered", outputCol="rawFeatures", numFeatures=10000)
idf = IDF(inputCol="rawFeatures", outputCol="features")

# ===== 6. TRAIN 3 MÔ HÌNH =====
models = {
    "Logistic Regression": LogisticRegression(
        featuresCol="features", labelCol="label_num", maxIter=100
    ),
    "Naive Bayes": NaiveBayes(
        featuresCol="features", labelCol="label_num"
    ),
    "Random Forest": RandomForestClassifier(
        featuresCol="features", labelCol="label_num", numTrees=50
    )
}

evaluator_acc = MulticlassClassificationEvaluator(
    labelCol="label_num", predictionCol="prediction", metricName="accuracy"
)
evaluator_f1 = MulticlassClassificationEvaluator(
    labelCol="label_num", predictionCol="prediction", metricName="f1"
)
evaluator_p = MulticlassClassificationEvaluator(
    labelCol="label_num", predictionCol="prediction", metricName="weightedPrecision"
)
evaluator_r = MulticlassClassificationEvaluator(
    labelCol="label_num", predictionCol="prediction", metricName="weightedRecall"
)
results = {}

for name, classifier in models.items():
    print(f"\n⏳ Đang train {name}...")

    pipeline = Pipeline(stages=[tokenizer, remover, hashingTF, idf, classifier])
    model = pipeline.fit(train_df)
    predictions = model.transform(test_df)

    acc       = evaluator_acc.evaluate(predictions)
    f1        = evaluator_f1.evaluate(predictions)
    precision = evaluator_p.evaluate(predictions)
    recall    = evaluator_r.evaluate(predictions)

    results[name] = {
        "Accuracy":  round(acc, 4),
        "F1-score":  round(f1, 4),
        "Precision": round(precision, 4),
        "Recall":    round(recall, 4)
    }
    print(f"✅ {name} — Accuracy: {acc:.4f} | F1: {f1:.4f} | Precision: {precision:.4f} | Recall: {recall:.4f}")

    # Lưu model tốt nhất
    if name == "Logistic Regression":
        model.write().overwrite().save("../tv3_ml/saved_model/logistic_regression")


# ===== 7. IN BẢNG SO SÁNH =====
print("\n===== KẾT QUẢ SO SÁNH =====")
results_df = pd.DataFrame(results).T
print(results_df)

# ===== 8. VẼ BIỂU ĐỒ =====
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

results_df["Accuracy"].plot(kind="bar", ax=axes[0], color=["#4C9BE8","#E87B4C","#4CE87B"])
axes[0].set_title("Accuracy so sánh các mô hình")
axes[0].set_ylabel("Accuracy")
axes[0].set_ylim(0, 1)
axes[0].tick_params(axis='x', rotation=30)

results_df["F1-score"].plot(kind="bar", ax=axes[1], color=["#4C9BE8","#E87B4C","#4CE87B"])
axes[1].set_title("F1-score so sánh các mô hình")
axes[1].set_ylabel("F1-score")
axes[1].set_ylim(0, 1)
axes[1].tick_params(axis='x', rotation=30)

plt.tight_layout()
plt.savefig("../tv3_ml/model_comparison.png", dpi=150)
print("\n✅ Biểu đồ đã lưu tại tv3_ml/model_comparison.png")

spark.stop()
