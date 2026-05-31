from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.ml.feature import Tokenizer, StopWordsRemover, HashingTF, IDF, StringIndexer
from pyspark.ml import Pipeline

HDFS_INPUT  = "hdfs://localhost:9001/fakenews/raw/final_data.csv"
HDFS_OUTPUT = "hdfs://localhost:9001/fakenews/nlp_features"
HDFS_MODEL  = "hdfs://localhost:9001/fakenews/models/tfidf_pipeline"

spark = SparkSession.builder \
    .appName("FakeNewsNLPPreprocessing") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# Đọc CSV từ HDFS
df = spark.read.csv(HDFS_INPUT, header=True, inferSchema=True)
print(f"Số bài đọc được: {df.count()}")

# Làm sạch text
df = df \
    .withColumn("content", F.lower(F.col("content"))) \
    .withColumn("content", F.regexp_replace(F.col("content"), r"https?://\S+", " ")) \
    .withColumn("content", F.regexp_replace(F.col("content"), r"[^a-zA-Z\s]", " ")) \
    .withColumn("content", F.regexp_replace(F.col("content"), r"\s+", " ")) \
    .withColumn("content", F.trim(F.col("content"))) \
    .filter(F.length(F.col("content")) > 20)

print(f"Sau làm sạch: {df.count()} bài")

# Pipeline TF-IDF
tokenizer = Tokenizer(inputCol="content", outputCol="words")
remover   = StopWordsRemover(inputCol="words", outputCol="filtered")
hashingTF = HashingTF(inputCol="filtered", outputCol="rawFeatures", numFeatures=10000)
idf       = IDF(inputCol="rawFeatures", outputCol="features")
indexer   = StringIndexer(inputCol="label", outputCol="label_idx")

pipeline = Pipeline(stages=[tokenizer, remover, hashingTF, idf, indexer])

model = pipeline.fit(df)
df_transformed = model.transform(df)

# Lưu features lên HDFS cho TV3
df_final = df_transformed.select("content", "features", "label_idx")
df_final.write.mode("overwrite").parquet(HDFS_OUTPUT)
print(f"Đã lưu TF-IDF features: {HDFS_OUTPUT}")

# Lưu model
model.write().overwrite().save(HDFS_MODEL)
print(f"Đã lưu pipeline model: {HDFS_MODEL}")

spark.stop()
