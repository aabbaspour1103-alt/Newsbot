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


    "Reuters Market": {
        "category": "USA Market",
        "url":
        "https://news.google.com/rss/search?q=Reuters+market+economy+Fed"
    },

    "CNBC": {
        "category": "USA Market",
        "url":
        "https://news.google.com/rss/search?q=CNBC+markets+stocks"
    },

    "Yahoo Finance": {
        "category": "USA Market",
        "url":
        "https://news.google.com/rss/search?q=Yahoo+Finance+Federal+Reserve"
    },


    "Trump News": {
        "category": "Trump Alert",
        "url":
        "https://news.google.com/rss/search?q=Donald+Trump+White+House"
    },


    "Fed News": {
        "category": "Trump/Fed Alert",
        "url":
        "https://news.google.com/rss/search?q=Federal+Reserve+Jerome+Powell+interest+rates"
    }

}



# خبرهای مهم

MARKET_KEYWORDS = [

    "Trump",
    "Donald Trump",
    "White House",
    "Federal Reserve",
    "Fed",
    "Jerome Powell",
    "interest rate",
    "inflation",
    "CPI",
    "SEC",
    "ETF",
    "Bitcoin",
    "crypto",
    "tariff",
    "sanction",
    "oil",
    "gold",
    "dollar"

]



# خبرهای بسیار مهم و فوری

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
    "Mozilla/5.0 Chrome/120 Safari/537.36",

    "Accept":
    "application/rss+xml, application/xml"

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
            data[-500:],
            f,
            ensure_ascii=False,
            indent=2
        )




def create_id(text):

    return hashlib.md5(
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

    for word in keywords:

        if word.lower() in text:

            return True

    return False




def check_impact(text):

    return check_keyword(
        text,
        MARKET_KEYWORDS
    )




def check_urgent(text):

    return check_keyword(
        text,
        URGENT_KEYWORDS
    )




def get_feed(source, data):

    news = []


    try:

        response = requests.get(
            data["url"],
            headers=HEADERS,
            timeout=20
        )

        response.raise_for_status()



        soup = BeautifulSoup(
            response.content,
            "lxml-xml"
        )


        items = soup.find_all(
            "item"
        )



        for item in items[:10]:

            title_tag = item.find("title")
            link_tag = item.find("link")
            description_tag = item.find("description")


            title = clean_text(
                title_tag.text
                if title_tag
                else ""
            )


            link = (
                link_tag.text.strip()
                if link_tag
                else ""
            )


            description = clean_text(
                description_tag.text
                if description_tag
                else ""
            )


            if title and link:


                full_text = (
                    title
                    +
                    " "
                    +
                    description
                )


                news.append({

                    "id":
                    create_id(link),

                    "source":
                    source,

                    "category":
                    data["category"],

                    "title":
                    title,

                    "description":
                    description[:800],

                    "link":
                    link,

                    "impact":
                    check_impact(
                        full_text
                    ),

                    "urgent":
                    check_urgent(
                        full_text
                    ),

                    "time":
                    datetime.now().isoformat()

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

        result = get_feed(
            source,
            data
        )


        for item in result:

            if item["id"] not in seen:

                all_news.append(
                    item
                )

                seen.append(
                    item["id"]
                )



    save_seen(
        seen
    )



    # اولویت:
    # فوری > مهم > عادی

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
        f"تعداد خبرهای دریافت شده: {len(news)}"
    )


    for item in news:

        print("\n🆕 خبر جدید")

        print(
            "📂 دسته:",
            item["category"]
        )

        print(
            "🚨 فوری:",
            item["urgent"]
        )

        print(
            "⚠️ مهم:",
            item["impact"]
        )

        print(
            "عنوان:",
            item["title"]
        )

        print(
            "خلاصه:",
            item["description"]
        )

        print("-" * 50)
