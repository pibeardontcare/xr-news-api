from flask import Flask, jsonify
import requests
from datetime import datetime
from dateutil.relativedelta import relativedelta, MO
from newspaper import Article
import os

app = Flask(__name__)

# === CONFIG ===
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
if not NEWS_API_KEY:
    raise ValueError("⚠️ NEWS_API_KEY environment variable not set.")
QUERY = '"XR" OR "Extended Reality" OR "AR" OR "VR" AND "AI"'
LANGUAGE = 'en'
MAX_ARTICLES = 20

# === DATE RANGE ===
today = datetime.today()
last_monday = today + relativedelta(weekday=MO(-1))
from_date = last_monday.strftime('%Y-%m-%d')
to_date = today.strftime('%Y-%m-%d')

# === GET ARTICLES ===
def get_articles():
    url = f'https://newsapi.org/v2/everything'
    params = {
        'q': QUERY,
        'from': from_date,
        'to': to_date,
        'sortBy': 'publishedAt',
        'language': LANGUAGE,
        'pageSize': MAX_ARTICLES,
        'apiKey': NEWS_API_KEY
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()['articles']

# === CLEAN CONTENT ===
def extract_article_content(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text.strip()
    except Exception as e:
        print(f"Error parsing {url}: {e}")
        return None

# === FLASK ROUTE ===
@app.route("/articles")
def articles():
    print(f"📅 Fetching XR/AI news from {from_date} to {to_date}...")
    raw_articles = get_articles()
    output = []

    for item in raw_articles:
        title = item['title']
        source = item['source']['name']
        url = item['url']
        published_at = item['publishedAt'][:10]
        content = extract_article_content(url)

        if content:
            print(f"📰 {title} ({source})")
            output.append({
                'title': title,
                'source': source,
                'url': url,
                'date': published_at,
                'content': content
            })

    return jsonify(output)

# === ENTRY POINT ===
if __name__ == "__main__":
    app.run(debug=True)
