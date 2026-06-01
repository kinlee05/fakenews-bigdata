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

## 8. chạy mô hình machine learning (tv3)
### yêu cầu 
- Dataset đã được xử lý ở bước 4 (`final_data.csv`)
- Java đã được cài đặt
Cài Java nếu chưa có:sudo apt install default-jdk -y
export JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64
export PATH=JAVAHOME/bin:JAVA_HOME/bin:
JAVAH​OME/bin:PATH
Cài thư viện Python:
pip install pyspark matplotlib pandas --break-system-packages
### chạy train 3 mô hình 
cd tv3_ml/
python3 train_model.py
### Kết quả sau khi chạy:
- Bảng so sánh 3 mô hình in ra terminal
- Biểu đồ lưu tại `tv3_ml/model_comparison.png`
- Model tốt nhất lưu tại `tv3_ml/saved_model/logistic_regression`
### Lưu model lên HDFS** (để TV4 sử dụng):
docker cp tv3_ml/saved_model namenode:/tmp/saved_model
docker exec namenode hdfs dfs -mkdir -p /fakenews/models
docker exec namenode hdfs dfs -put /tmp/saved_model /fakenews/models/

9. Chạy TV4 - Web App

**Yêu cầu:**
- Model đã được train ở bước 8 (`tv3_ml/model.pkl`)

**Cài thư viện:**
```bash
pip install fastapi uvicorn streamlit requests joblib --break-system-packages
```

**Terminal 1 - Chạy API:**
```bash
cd tv4_app/
uvicorn api:app --host 0.0.0.0 --port 8000
```

**Terminal 2 - Chạy Web App:**
```bash
cd tv4_app/
streamlit run app.py --server.port 8501
```

**Truy cập:** http://localhost:8501

**Kiểm tra API:**
```bash
curl http://localhost:8000/health
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "Aliens have landed in the USA"}'
```
