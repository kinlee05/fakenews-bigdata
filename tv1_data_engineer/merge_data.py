import pandas as pd

# Đọc 2 nguồn
df_kaggle = pd.read_csv("cleaned_data.csv")[["content", "label"]]
df_news = pd.read_csv("newsapi_data.csv")[["content", "label"]]

# Gộp lại
df_final = pd.concat([df_kaggle, df_news], ignore_index=True)
df_final = df_final.dropna(subset=["content", "label"])
df_final = df_final.drop_duplicates(subset=["content"])
df_final = df_final.reset_index(drop=True)

print("Tổng:", df_final.shape[0])
print(df_final["label"].value_counts())

df_final.to_csv("final_data.csv", index=False)
print("Đã lưu final_data.csv")
