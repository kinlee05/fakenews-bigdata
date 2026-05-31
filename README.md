# Fake News Detection - Big Data Project

## Thành viên nhóm
- TV1: Data Engineer
- TV2: Pipeline Engineer
- TV3: ML Engineer
- TV4: Full-stack + Report

## Cách chạy
## 1. Clone repo
git clone https://github.com/kinlee05/fakenews-bigdata.git
cd fakenews-bigdata

## 2. Tải dataset
- Tải file `Fake.csv` và `True.csv` từ Google Drive: https://drive.google.com/drive/folders/1fBaebU46UxJWNKNT74jGapFnR5rpREX1?usp=drive_link
- Đặt 2 file vào thư mục `tv1_data_engineer/`

## 3. Chạy môi trường
###Tạo file `hadoop.env` trong thư mục gốc với nội dung sau:
cat > hadoop.env << 'EOF'
CORE_CONF_fs_defaultFS=hdfs://namenode:9000
CORE_CONF_hadoop_http_staticuser_user=root
HDFS_CONF_dfs_replication=1
EOF
### Chạy docker compose
docker compose up -d
### Kiểm tra container
docker ps

## 4. Chuẩn bị dữ liệu
cd tv1_data_engineer/
python3 clean_data.py
###Lưu ý: Mở file crawl_newsapi.py, thay API_KEY bằng key của bạn
python3 crawl_newsapi.py
python3 merge_data.py
python3 clean_text.py

## 5. Upload lên HDFS
docker cp tv1_data_engineer/final_data.csv namenode:/tmp/
docker exec namenode hdfs dfs -mkdir -p /fakenews/raw
docker exec namenode hdfs dfs -put /tmp/final_data.csv /fakenews/raw/
docker exec namenode hdfs dfs -ls /fakenews/raw/

## 6. Chạy Kafka Producer
### Terminal 1 - Start Kafka:
bashcd ~/kafka_2.13-4.0.1
bin/kafka-storage.sh format --standalone -t $(bin/kafka-storage.sh random-uuid) -c config/server.properties
bin/kafka-server-start.sh config/server.properties
### Terminal 2 - Tạo topic:
bashbin/kafka-topics.sh --create \
  --topic fakenews-topic \
  --bootstrap-server localhost:9092 \
  --partitions 1 \
  --replication-factor 1
### Terminal 3 - Chạy producer:
bashcd tv1_data_engineer/
python3 kafka_producer.py

## 7.Chạy TV2 Pipeline
Thoát HDFS safe mode:
bashdocker exec -it namenode hdfs dfsadmin -safemode leave
docker exec -it namenode hdfs dfs -chmod -R 777 /fakenews

### Terminal 4 - Chạy Spark Structured Streaming (chạy trước, giữ chạy):
bashcd tv2_pipeline/
/home/hdoop/spark/bin/spark-submit \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0 \
  spark_structured_streaming.py
  
### Terminal 5 - Chạy Producer TV2:
bashcd tv2_pipeline/
python3 kafka_producer.py

### Terminal 5 - Chạy Consumer:
bashpython3 kafka_consumer.py
Sau khi Producer xong, dừng Streaming (Ctrl+C), rồi chạy tiếp:
bash/home/hdoop/spark/bin/spark-submit spark_pipeline.py
bash/home/hdoop/spark/bin/spark-submit nlp_preprocessing.py

### Kiểm tra kết quả trên HDFS:
bashdocker exec -it namenode hdfs dfs -ls /fakenews/processed/
docker exec -it namenode hdfs dfs -ls /fakenews/nlp_features/
docker exec -it namenode hdfs dfs -ls /fakenews/streaming_output/
