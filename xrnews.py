from flask import Flask, jsonify
import requests
from datetime import datetime
from dateutil.relativedelta import relativedelta, MO
import os

from dotenv import load_dotenv
load_dotenv()

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




# === FLASK ROUTE ===

@app.route("/articles")
def articles():
    # === Fresh DATE RANGE on every call ===
    today = datetime.today()
    last_monday = today + relativedelta(weekday=MO(-1))
    from_date = last_monday.strftime('%Y-%m-%d')
    to_date = today.strftime('%Y-%m-%d')

    print(f"📅 Fetching XR/AI news from {from_date} to {to_date}...")

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

    raw_articles = get_articles()
    output = []

    for item in raw_articles:
        title = item['title']
        source = item['source']['name']
        url = item['url']
        published_at = item['publishedAt'][:10]
        content = item.get('description') or item.get('content') or "No summary available"

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
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

