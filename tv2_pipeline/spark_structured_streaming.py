from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, StringType

KAFKA_BROKER    = "localhost:9092"
KAFKA_TOPIC     = "fakenews-topic"
HDFS_OUTPUT     = "hdfs://localhost:9001/fakenews/streaming_output"
HDFS_CHECKPOINT = "/tmp/fakenews/checkpoints"

schema = StructType([
    StructField("id",      StringType(), True),
    StructField("content", StringType(), True),
    StructField("label",   StringType(), True),
])

spark = SparkSession.builder \
    .appName("FakeNewsStructuredStreaming") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.0") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

raw_stream = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BROKER) \
    .option("subscribe", KAFKA_TOPIC) \
    .option("startingOffsets", "earliest") \
    .option("failOnDataLoss", "false") \
    .load()

parsed = raw_stream \
    .select(F.col("value").cast("string").alias("json_str")) \
    .select(F.from_json(F.col("json_str"), schema).alias("data")) \
    .select("data.*") \
    .filter(F.col("content").isNotNull() & F.col("label").isNotNull()) \
    .withColumn("content", F.trim(F.col("content"))) \
    .withColumn("processed_at", F.current_timestamp())

def write_batch(batch_df, batch_id):
    count = batch_df.count()
    if count == 0:
        print(f"[Batch {batch_id}] Không có dữ liệu mới.")
        return
    print(f"[Batch {batch_id}] Xử lý {count} bài")
    batch_df.write.mode("append").parquet(HDFS_OUTPUT)

query = parsed.writeStream \
    .outputMode("append") \
    .option("checkpointLocation", HDFS_CHECKPOINT) \
    .trigger(processingTime="30 seconds") \
    .foreachBatch(write_batch) \
    .start()

print("Streaming đang chạy... (Ctrl+C để dừng)")
query.awaitTermination()
