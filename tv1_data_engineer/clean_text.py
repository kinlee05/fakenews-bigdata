import pandas as pd
import re

df = pd.read_csv("final_data.csv")

def clean_text(text):
    text = str(text).lower()                        # lowercase
    text = re.sub(r"http\S+", "", text)             # xóa URL
    text = re.sub(r"<.*?>", "", text)               # xóa HTML tags
    text = re.sub(r"[^a-z\s]", "", text)            # chỉ giữ chữ cái
    text = re.sub(r"\s+", " ", text).strip()        # xóa khoảng trắng thừa
    return text

df["content"] = df["content"].apply(clean_text)
df = df[df["content"].str.len() > 50]  # xóa bài quá ngắn
df = df.reset_index(drop=True)

print("Sau khi làm sạch text:", df.shape[0], "dòng")
print(df["content"][0][:200])  # xem thử

df.to_csv("final_data.csv", index=False)
print("Đã lưu lại final_data.csv")
