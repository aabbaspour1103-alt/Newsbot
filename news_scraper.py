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


    "Reuters Market": {
        "category": "Global Market",
        "url":
        "https://news.google.com/rss/search?q=Reuters+market+economy+Fed"
    },

    "Bloomberg Market": {
        "category": "Global Market",
        "url":
        "https://news.google.com/rss/search?q=Bloomberg+markets+economy"
    },

    "MarketWatch": {
        "category": "USA Market",
        "url":
        "https://news.google.com/rss/search?q=MarketWatch+stocks+Federal+Reserve"
    },

    "CNBC": {
        "category": "USA Market",
        "url":
        "https://news.google.com/rss/search?q=CNBC+markets+stocks"
    },


    "Trump Alert": {
        "category": "Trump",
        "url":
        "https://news.google.com/rss/search?q=Donald+Trump+White+House"
    },


    "Federal Reserve": {
        "category": "FED",
        "url":
        "https://news.google.com/rss/search?q=Federal+Reserve+Jerome+Powell+interest+rates"
    }

}



MARKET_KEYWORDS = [

    "Trump",
    "Donald Trump",
    "White House",
    "Federal Reserve",
    "Fed",
    "Powell",
    "interest rate",
    "inflation",
    "CPI",
    "SEC",
    "ETF",
    "Bitcoin",
    "Ethereum",
    "crypto",
    "tariff",
    "sanction",
    "oil",
    "gold",
    "dollar",
    "stock",
    "market"

]


URGENT_KEYWORDS = [

    "war",
    "attack",
    "invasion",
    "crisis",
    "emergency",
    "collapse",
    "bank failure",
    "market crash",
    "global crisis",
    "Trump announces",
    "Trump signs",
    "Fed emergency",
    "emergency meeting",
    "rate cut",
    "rate hike",
    "ETF approved",
    "Bitcoin ETF approved",
    "SEC approves",
    "major sanctions"

]



HEADERS = {

    "User-Agent":
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",

    "Accept":
    "application/rss+xml, application/xml,text/xml"

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
            ensure_ascii=False,
            indent=2
        )




def create_id(title, link):

    text = title + link

    return hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()




def clean_text(text):

    if not text:
        return ""

    soup = BeautifulSoup(
        text,
        "html.parser"
    )

    return soup.get_text(
        " ",
        strip=True
    )




def check_keyword(text, keywords):

    text = text.lower()

    return any(
        word.lower() in text
        for word in keywords
    )




def get_feed(source, data):

    news = []

    try:

        response = requests.get(
            data["url"],
            headers=HEADERS,
            timeout=25
        )

        response.raise_for_status()


        soup = BeautifulSoup(
            response.content,
            "xml"
        )


        for item in soup.find_all("item")[:15]:

            title = clean_text(
                item.title.text
                if item.title
                else ""
            )


            link = (
                item.link.text.strip()
                if item.link
                else ""
            )


            description = clean_text(
                item.description.text
                if item.description
                else ""
            )


            if not title or not link:
                continue


            text = title + " " + description


            news.append({

                "id":
                create_id(title, link),

                "source":
                source,

                "category":
                data["category"],

                "title":
                title,

                "description":
                description[:700],

                "link":
                link,

                "urgent":
                check_keyword(
                    text,
                    URGENT_KEYWORDS
                ),

                "impact":
                check_keyword(
                    text,
                    MARKET_KEYWORDS
                ),

                "time":
                datetime.utcnow().isoformat()

            })


    except Exception as e:

        print(
            f"خطا در {source}: {e}"
        )


    return news




def get_news(limit=50):

    all_news = []

    seen = load_seen()


    for source, data in NEWS_SOURCES.items():

        feeds = get_feed(
            source,
            data
        )


        for item in feeds:

            if item["id"] not in seen:

                all_news.append(item)

                seen.append(
                    item["id"]
                )


    save_seen(seen)



    all_news.sort(
        key=lambda x:
        (
            x["urgent"],
            x["impact"]
        ),
        reverse=True
    )


    return all_news[:limit]




if __name__ == "__main__":

    news = get_news()


    print(
        f"تعداد خبرهای جدید: {len(news)}"
    )


    for n in news:

        print("\n🆕 خبر")

        print(
            "📂",
            n["category"]
        )

        print(
            "🚨 فوری:",
            n["urgent"]
        )

        print(
            "⚠️ مهم:",
            n["impact"]
        )

        print(
            n["title"]
        )

        print(
            n["link"]
        )

        print("-"*50)
