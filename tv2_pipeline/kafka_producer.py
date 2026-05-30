import pandas as pd
import json
import time
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

df = pd.read_csv("/home/hdoop/fakenews_project/final_data.csv")

print(f"Bắt đầu gửi {len(df)} bài lên Kafka...")

for i, row in df.iterrows():
    message = {
        "id": str(i),
        "content": str(row["content"]),
        "label": str(row["label"])
    }
    producer.send("fakenews-topic", message)
    
    if i % 1000 == 0:
        print(f"Đã gửi {i}/{len(df)} bài")
    
    time.sleep(0.01)

producer.flush()
print("Gửi xong toàn bộ dữ liệu!")
