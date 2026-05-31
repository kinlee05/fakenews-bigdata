from pyspark.sql import SparkSession
from pyspark.ml.feature import Tokenizer, StopWordsRemover, HashingTF, IDF, StringIndexer
from pyspark.ml import Pipeline

spark = SparkSession.builder \
    .appName("FakeNewsPreprocessing") \
    .getOrCreate()

# Đọc data từ HDFS
df = spark.read.csv(
    "hdfs://localhost:9001/fakenews/raw/final_data.csv",
    header=True,
    inferSchema=True
)

print("Số dòng:", df.count())
df.show(5)

# TF-IDF Pipeline
tokenizer = Tokenizer(inputCol="content", outputCol="words")
remover = StopWordsRemover(inputCol="words", outputCol="filtered")
hashingTF = HashingTF(inputCol="filtered", outputCol="rawFeatures", numFeatures=10000)
idf = IDF(inputCol="rawFeatures", outputCol="features")
indexer = StringIndexer(inputCol="label", outputCol="label_idx")

pipeline = Pipeline(stages=[tokenizer, remover, hashingTF, idf, indexer])

# Fit và transform
model = pipeline.fit(df)
df_transformed = model.transform(df)

# Lưu kết quả lên HDFS
df_final = df_transformed.select("features", "label_idx")
df_final.write.mode("overwrite").parquet(
    "hdfs://localhost:9001/fakenews/processed/"
)
print("Đã lưu processed data lên HDFS!")

