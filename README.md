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
- Tải file `Fake.csv` và `True.csv` từ Google Drive: https://drive.google.com/drive/folders/1fBaebU46UxJWNKNT74jGapFnR5rpREX1?usp=drive_link
- Đặt 2 file vào thư mục `tv1_data_engineer/`

### 3. Chạy môi trường
# Chạy docker compose
docker compose up -d
# Kiểm tra container
docker ps

### 4. Chuẩn bị dữ liệu
cd tv1_data_engineer/
python3 clean_data.py
#Lưu ý: Mở file crawl_newsapi.py, thay API_KEY bằng key của bạn
python3 crawl_newsapi.py
python3 merge_data.py
python3 clean_text.py

### 5. Upload lên HDFS
docker cp tv1_data_engineer/final_data.csv namenode:/tmp/
docker exec namenode hdfs dfs -mkdir -p /fakenews/raw
docker exec namenode hdfs dfs -put /tmp/final_data.csv /fakenews/raw/
docker exec namenode hdfs dfs -ls /fakenews/raw/

### 6. Chạy Kafka Producer
# Terminal 1 - Start Kafka
cd ~/kafka_2.13-4.3.0
bin/kafka-storage.sh format --standalone -t $(bin/kafka-storage.sh random-uuid) -c config/server.properties
bin/kafka-server-start.sh config/server.properties

# Terminal 2 - Tạo topic
kafka-topics.sh --create --topic fakenews-topic --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1

# Terminal 3 - Chạy producer
cd tv1_data_engineer/
python3 kafka_producer.py
