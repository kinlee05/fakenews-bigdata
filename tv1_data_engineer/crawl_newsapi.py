import requests

import pandas as pd

API_KEY = "f51163d39aa8487e9465200cbf2ec86c"  # thay key vào đây

# Lấy tin thật từ các nguồn uy tín

urls = [

    f"https://newsapi.org/v2/top-headlines?sources=reuters&pageSize=100&apiKey={API_KEY}",

    f"https://newsapi.org/v2/top-headlines?sources=bbc-news&pageSize=100&apiKey={API_KEY}",

    f"https://newsapi.org/v2/top-headlines?sources=cnn&pageSize=100&apiKey={API_KEY}",

]

articles = []

for url in urls:

    response = requests.get(url)

    data = response.json()

    print(data["status"], "-", len(data.get("articles", [])), "articles")

    for a in data.get("articles", []):

        if a["title"] and a["description"]:

            articles.append({

                "content": a["title"] + " " + (a["description"] or ""),

                "label": "REAL",

                "source": a["source"]["name"]

            })

df_news = pd.DataFrame(articles)

print("NewsAPI:", df_news.shape[0], "bài")

df_news.to_csv("newsapi_data.csv", index=False)

print("Đã lưu newsapi_data.csv")
