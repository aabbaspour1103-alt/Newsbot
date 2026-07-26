import requests
import json
import os
import hashlib

from bs4 import BeautifulSoup
from datetime import datetime


NEWS_SOURCES = {

    "CoinDesk": {
        "category": "Crypto",
        "url": "https://www.coindesk.com/arc/outboundfeeds/rss/"
    },

    "Cointelegraph": {
        "category": "Crypto",
        "url": "https://cointelegraph.com/rss"
    },

    "Decrypt": {
        "category": "Crypto",
        "url": "https://decrypt.co/feed"
    },

    "CryptoSlate": {
        "category": "Crypto",
        "url": "https://cryptoslate.com/feed/"
    },

    "The Block": {
        "category": "Crypto",
        "url": "https://www.theblock.co/rss.xml"
    },

    "Bitcoin Magazine": {
        "category": "Crypto",
        "url": "https://bitcoinmagazine.com/.rss/full/"
    },

    "Reuters": {
        "category": "Market",
        "url": "https://news.google.com/rss/search?q=Reuters+market+economy"
    },

    "Bloomberg": {
        "category": "Market",
        "url": "https://news.google.com/rss/search?q=Bloomberg+markets"
    },

    "CNBC": {
        "category": "Market",
        "url": "https://news.google.com/rss/search?q=CNBC+stocks"
    },

    "Federal Reserve": {
        "category": "FED",
        "url": "https://news.google.com/rss/search?q=Federal+Reserve+Powell+interest+rates"
    },

    "Trump": {
        "category": "Politics",
        "url": "https://news.google.com/rss/search?q=Donald+Trump+White+House"
    }
}



MARKET_WORDS = [
    "bitcoin",
    "ethereum",
    "crypto",
    "ETF",
    "SEC",
    "Fed",
    "Federal Reserve",
    "Powell",
    "interest rate",
    "inflation",
    "CPI",
    "GDP",
    "Trump",
    "tariff",
    "gold",
    "oil",
    "dollar",
    "stock",
    "market"
]


URGENT_WORDS = [
    "breaking",
    "crisis",
    "war",
    "attack",
    "collapse",
    "bank failure",
    "market crash",
    "emergency",
    "rate cut",
    "rate hike",
    "ETF approved",
    "SEC approves"
]


HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


SEEN_FILE = "seen_news.json"



def load_seen():

    if os.path.exists(SEEN_FILE):

        try:

            with open(
                SEEN_FILE,
                "r",
                encoding="utf-8"
            ) as f:

                return json.load(f)

        except:

            return []

    return []



def save_seen(data):

    with open(
        SEEN_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data[-1000:],
            f,
            ensure_ascii=False
        )



def make_id(title):

    return hashlib.sha256(
        title.lower().encode("utf-8")
    ).hexdigest()



def clean(text):

    if not text:
        return ""

    return BeautifulSoup(
        text,
        "html.parser"
    ).get_text(
        " ",
        strip=True
    )



def has_word(text, words):

    text = text.lower()

    return any(
        w.lower() in text
        for w in words
    )



def get_feed(source, data):

    result = []

    try:

        r = requests.get(
            data["url"],
            headers=HEADERS,
            timeout=20
        )

        soup = BeautifulSoup(
            r.content,
            "xml"
        )

        items = soup.find_all("item")


        for item in items[:10]:

            ifdef get_news(limit=50):

    news = []

    seen = load_seen()


    for source, data in NEWS_SOURCES.items():

        items = get_feed(
            source,
            data
        )


        for item in items:

            if item["id"] not in seen:

                news.append(item)

                seen.append(
                    item["id"]
                )


    save_seen(
        seen
    )


    news.sort(
        key=lambda x: (
            x["urgent"],
            x["impact"],
            x["time"]
        ),
        reverse=True
    )


    return news[:limit]



def get_best_news(limit=10):

    news = get_news(
        limit
    )


    important = [

        n for n in news

        if n["urgent"] or n["impact"]

    ]


    if important:

        return important[:limit]


    return news[:limit]



def telegram_text(item):

    text = f"""
📰 {item['source']}

📂 دسته:
{item['category']}

{"🚨 خبر فوری" if item['urgent'] else "📝 خبر بازار"}

{item['title']}
"""


    if item["description"]:

        text += (
            "\n📄 "
            +
            item["description"]
        )


    if item["link"]:

        text += (
            "\n\n🔗 "
            +
            item["link"]
        )


    return text.strip()



def get_telegram_news(limit=5):

    news = get_best_news(
        limit
    )


    return [

        telegram_text(item)

        for item in news

    ]



if __name__ == "__main__":

    news = get_news()


    print(
        f"تعداد خبرهای جدید: {len(news)}"
    )


    for item in news:

        print("\n" + "-" * 50)

        print(
            item["source"]
        )

        print(
            item["title"]
        )

        print(
            item["link"]
        )
