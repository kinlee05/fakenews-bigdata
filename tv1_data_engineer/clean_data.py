import pandas as pd

# Đọc 2 file
fake = pd.read_csv("Fake.csv")
true = pd.read_csv("True.csv")

# Gán label
fake["label"] = "FAKE"
true["label"] = "REAL"

# Gộp lại
df = pd.concat([fake, true], ignore_index=True)

# Chỉ giữ cột cần thiết
df = df[["title", "text", "subject", "date", "label"]]

# Gộp title + text thành 1 cột content
df["content"] = df["title"] + " " + df["text"]

# Làm sạch
df = df.dropna(subset=["content", "label"])
df = df.drop_duplicates(subset=["content"])
df = df.reset_index(drop=True)

# Kiểm tra
print("Tổng số dòng:", df.shape[0])
print(df["label"].value_counts())
print(df.head(2))

# Lưu ra file
df.to_csv("cleaned_data.csv", index=False)
print("Đã lưu cleaned_data.csv")
