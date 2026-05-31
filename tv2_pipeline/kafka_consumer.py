from confluent_kafka import Consumer
import json

consumer = Consumer({
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'fakenews-consumer-group',
    'auto.offset.reset': 'earliest'
})

consumer.subscribe(['fakenews-topic'])

messages = []
print("Bắt đầu consume từ Kafka topic: fakenews-topic...")

try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            if len(messages) > 0:
                print(f"Không còn message mới. Tổng đã nhận: {len(messages)}")
                break
            continue
        if msg.error():
            print(f"Lỗi: {msg.error()}")
            continue

        data = json.loads(msg.value().decode('utf-8'))
        messages.append(data)

        if len(messages) % 1000 == 0:
            print(f"Đã nhận {len(messages)} bài | offset={msg.offset()}")

        if len(messages) >= 10000:
            print(f"Đã nhận đủ {len(messages)} bài. Dừng.")
            break
finally:
    consumer.close()
    print(f"Tổng cộng đã consume: {len(messages)} bài")
