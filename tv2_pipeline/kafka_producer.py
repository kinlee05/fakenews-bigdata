import pandas as pd
import json
import time
from confluent_kafka import Producer

producer = Producer({'bootstrap.servers': 'localhost:9092'})

df = pd.read_csv("/home/hdoop/Documents/fakenews-bigdata/tv1_data_engineer/final_data.csv")
print(f"Bắt đầu gửi {len(df)} bài lên Kafka...")

for i, row in df.iterrows():
    message = {
        "id": str(i),
        "content": str(row["content"]),
        "label": str(row["label"])
    }
    producer.produce("fakenews-topic", json.dumps(message).encode("utf-8"))

    if i % 1000 == 0:
        producer.poll(0)
        print(f"Đã gửi {i}/{len(df)} bài")

    time.sleep(0.01)

producer.flush()
print("Gửi xong toàn bộ dữ liệu!")
