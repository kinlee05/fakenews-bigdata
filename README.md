# Fake News Detection - Big Data Project

## Thành viên nhóm
- TV1: Data Engineer
- TV2: Pipeline Engineer
- TV3: ML Engineer
- TV4: Full-stack + Report

## Cách chạy

### 1. Clone repo
git clone https://github.com/kinlee05/fakenews-bigdata.git
cd fakenews-bigdata

### 2. Tải dataset
- Tải từ Google Drive: https://drive.google.com/drive/folders/1fBaebU46UxJWNKNT74jGapFnR5rpREX1?usp=drive_link

### 3. Chạy môi trường
docker-compose up -d

### 4. Chuẩn bị dữ liệu
python3 clean_data.py
python3 crawl_newsapi.py
python3 merge_data.py
python3 clean_text.py

### 5. Upload lên HDFS
hdfs dfs -mkdir -p /fakenews/raw
hdfs dfs -put final_data.csv /fakenews/raw/

### 6. Chạy Kafka Producer
python3 kafka_producer.py
