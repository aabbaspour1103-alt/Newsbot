import requests
import json
import os
import hashlib
from bs4 import BeautifulSoup
from datetime import datetime


NEWS_SOURCES = {

    "CoinDesk": {
        "url": "https://www.coindesk.com/arc/outboundfeeds/rss/",
    },

    "Cointelegraph": {
        "url": "https://cointelegraph.com/rss",
    },

    "Decrypt": {
        "url": "https://decrypt.co/feed",
    },

    "CryptoSlate": {
        "url": "https://cryptoslate.com/feed/",
    },

    "NewsBTC": {
        "url": "https://www.newsbtc.com/feed/",
    },

    "CryptoPotato": {
        "url": "https://cryptopotato.com/feed/",
    }
}


HEADERS = {

    "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "Chrome/120.0 Safari/537.36",

    "Accept":
        "application/rss+xml, application/xml, text/xml"

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



def get_feed(source, url):

    news = []

    try:

        response = requests.get(
            url,
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

            title_tag = item.find(
                "title"
            )

            link_tag = item.find(
                "link"
            )


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


            if title and link:

                news.append({

                    "id":
                        create_id(link),

                    "source":
                        source,

                    "title":
                        title,

                    "link":
                        link,

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
            data["url"]
        )


        for item in result:

            if item["id"] not in seen:

                all_news.append(item)

                seen.append(
                    item["id"]
                )


    save_seen(
        seen
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
            "📰 منبع:",
            item["source"]
        )

        print(
            "🇮🇷 عنوان:",
            item["title"]
        )

        print(
            "🔗 لینک:",
            item["link"]
        )

        print(
            "-" * 50
        )
