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
        "url": "https://news.google.com/rss/search?q=Reuters+market+economy+Fed"
    },

    "Bloomberg Market": {
        "category": "Global Market",
        "url": "https://news.google.com/rss/search?q=Bloomberg+markets+economy"
    },

    "MarketWatch": {
        "category": "USA Market",
        "url": "https://news.google.com/rss/search?q=MarketWatch+stocks+Federal+Reserve"
    },

    "CNBC": {
        "category": "USA Market",
        "url": "https://news.google.com/rss/search?q=CNBC+markets+stocks"
    },

    "Yahoo Finance": {
        "category": "Global Market",
        "url": "https://news.google.com/rss/search?q=Yahoo+Finance+stocks"
    },

    "Financial Times": {
        "category": "Global Market",
        "url": "https://news.google.com/rss/search?q=Financial+Times+markets"
    },

    "Wall Street Journal": {
        "category": "Global Market",
        "url": "https://news.google.com/rss/search?q=Wall+Street+Journal+markets"
    },

    "Barrons": {
        "category": "Global Market",
        "url": "https://news.google.com/rss/search?q=Barrons+markets"
    },

    "Investing.com": {
        "category": "Global Market",
        "url": "https://news.google.com/rss/search?q=Investing.com+markets"
    },


    "Trump Alert": {
        "category": "Trump",
        "url": "https://news.google.com/rss/search?q=Donald+Trump+White+House"
    },


    "Federal Reserve": {
        "category": "FED",
        "url": "https://news.google.com/rss/search?q=Federal+Reserve+Jerome+Powell+interest+rates"
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
    "PCE",
    "GDP",
    "FOMC",
    "ECB",
    "SEC",
    "ETF",
    "Bitcoin",
    "Ethereum",
    "Solana",
    "XRP",
    "USDT",
    "crypto",
    "tariff",
    "sanction",
    "oil",
    "gold",
    "dollar",
    "stock",
    "market",
    "Nasdaq",
    "S&P 500",
    "Dow Jones",
    "Treasury",
    "bond",
    "yield"

]



URGENT_KEYWORDS = [

    "breaking",
    "war",
    "attack",
    "missile",
    "invasion",
    "crisis",
    "emergency",
    "collapse",
    "bank failure",
    "bankruptcy",
    "liquidation",
    "market crash",
    "global crisis",
    "Trump announces",
    "Trump signs",
    "executive order",
    "Fed emergency",
    "emergency meeting",
    "Fed decision",
    "rate cut",
    "rate hike",
    "ETF approved",
    "Bitcoin ETF approved",
    "SEC approves",
    "major sanctions"

]


HEADERS = {

    "User-Agent":
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",

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

        except Exception:

            return []

    return []



def save_seen(data):

    try:

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

    except Exception:

        pass



def create_id(title, link):

    text = (
        title.strip().lower()
        +
        link.strip().lower()
    )

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

    if not text:

        return False

    text = text.lower()

    for word in keywords:

        if word.lower() in text:

            return True

    return False



def get_time():

    return datetime.utcnow().isoformat()



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


        items = soup.find_all("item")


        if not items:

            items = soup.find_all("entry")



        for item in items[:15]:


            title = ""

            if item.title:

                title = clean_text(
                    item.title.text
                )


            if len(title) < 20:

                continue



            link = ""


            if item.link:


                if item.link.has_attr("href"):

                    link = item.link["href"]

                else:

                    link = item.link.text.strip()



            if not link:

                continue



            description = ""


            if item.description:

                description = clean_text(
                    item.description.text
                )


            elif item.summary:

                description = clean_text(
                    item.summary.text
                )



            full_text = (
                title
                +
                " "
                +
                description
            )



            news.append({

                "id": create_id(
                    title,
                    link
                ),

                "source": source,

                "category": data["category"],

                "title": title,

                "description": description[:500],

                "link": link,

                "urgent": check_keyword(
                    full_text,
                    URGENT_KEYWORDS
                ),

                "impact": check_keyword(
                    full_text,
                    MARKET_KEYWORDS
                ),

                "time": get_time()

            })


    except Exception as e:

        print(
            f"خطا در دریافت {source}: {e}"
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



    save_seen(
        seen
    )



    all_news.sort(

        key=lambda x: (

            x["urgent"],

            x["impact"],

            x["time"]

        ),

        reverse=True

    )



    return all_news[:limit]



def format_news(news):

    result = []


    for item in news:


        result.append({

            "source":
            item["source"],


            "category":
            item["category"],


            "title":
            item["title"],


            "description":
            item["description"],


            "link":
            item["link"],


            "urgent":
            item["urgent"],


            "impact":
            item["impact"],


            "time":
            item["time"]

        })


    return result



if __name__ == "__main__":


    news = get_news()



    print(
        f"تعداد خبرهای جدید: {len(news)}"
    )



    for n in news:


        print("\n" + "=" * 60)


        print(
            "📰 منبع:",
            n["source"]
        )


        print(
            "📂 دسته:",
            n["category"]
        )


        print(
            "🚨 فوری:",
            "بله" if n["urgent"] else "خیر"
        )


        print(
            "⚠️ مهم:",
            "بله" if n["impact"] else "خیر"
        )


        print(
            "\n📝 عنوان:"
        )


        print(
            n["title"]
        )


        if n["description"]:


            print(
                "\n📄 توضیحات:"
            )


            print(
                n["description"]
            )



        print(
            "\n🔗 لینک:"
        )


        print(
            n["link"]
        )


        print(
            "\n⏰ زمان:"
        )


        print(
            n["time"]
        )
        def get_best_news(limit=10):

    news = get_news(
        limit=limit
    )


    important = []


    for item in news:


        if (
            item["urgent"]
            or
            item["impact"]
        ):

            important.append(item)



    if important:

        return important[:limit]


    return news[:limit]



def export_json(filename="latest_news.json"):

    news = get_best_news()


    try:

        with open(
            filename,
            "w",
            encoding="utf-8"
        ) as f:


            json.dump(

                news,

                f,

                ensure_ascii=False,

                indent=4

            )


        return True


    except Exception:


        return False



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


    messages = []


    for item in news:

        messages.append(
            telegram_text(item)
        )


    return messages
