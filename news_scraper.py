import feedparser
import hashlib
import json
import os
import re
from datetime import datetime, timezone


NEWS_SOURCES = {

    "CoinDesk": "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "Cointelegraph": "https://cointelegraph.com/rss",
    "Decrypt": "https://decrypt.co/feed",
    "The Block": "https://www.theblock.co/rss.xml",
    "CryptoSlate": "https://cryptoslate.com/feed/",
    "Bitcoin Magazine": "https://bitcoinmagazine.com/.rss/full/",

    "Bloomberg": "https://feeds.bloomberg.com/markets/news.rss",
    "CNBC": "https://www.cnbc.com/id/100003114/device/rss/rss.html",
    "Reuters": "https://feeds.reuters.com/reuters/businessNews",
}


SAVE_FILE = "sent_news.json"


URGENT_WORDS = [
    "Trump",
    "Federal Reserve",
    "Fed",
    "interest rate",
    "rate cut",
    "Bitcoin ETF",
    "SEC",
    "hack",
    "crash",
    "war",
    "sanctions",
    "breaking"
]



def load_sent():

    if not os.path.exists(SAVE_FILE):
        return []

    try:

        with open(
            SAVE_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)

    except:

        return []



def save_sent(data):

    with open(
        SAVE_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data[-1000:],
            f,
            ensure_ascii=False,
            indent=2
        )



def clean_text(text):

    if not text:
        return ""

    text = re.sub(
        "<.*?>",
        "",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()



def shorten(text, limit=350):

    if len(text) <= limit:
        return text

    return text[:limit] + "..."



def news_id(text):

    return hashlib.md5(
        text.lower().encode("utf-8")
    ).hexdigest()



def check_priority(text):

    text = text.lower()

    for word in URGENT_WORDS:

        if word.lower() in text:
            return True

    return False



def get_date(item):

    try:

        if hasattr(item, "published_parsed"):

            return datetime(
                *item.published_parsed[:6],
                tzinfo=timezone.utc
            )

    except:
        pass


    return datetime.min.replace(
        tzinfo=timezone.utc
    )



def is_recent(item):

    published = get_date(item)


    if published.year == 1:

        return True


    now = datetime.now(
        timezone.utc
    )


    hours = (
        now - published
    ).total_seconds() / 3600


    return hours <= 48




def get_news(limit=10):

    sent = load_sent()

    news = []


    for source, url in NEWS_SOURCES.items():

        try:

            feed = feedparser.parse(url)


            for item in feed.entries[:20]:


                if not is_recent(item):

                    continue



                title = clean_text(
                    item.get(
                        "title",
                        ""
                    )
                )


                if len(title) < 15:

                    continue



                uid = news_id(title)



                if uid in sent:

                    continue



                description = clean_text(
                    item.get(
                        "summary",
                        item.get(
                            "description",
                            ""
                        )
                    )
                )



                news.append({

                    "source": source,

                    "title": title,

                    "description": shorten(
                        description
                    ),

                    "urgent": check_priority(
                        title + " " + description
                    ),

                    "category": (
                        "Crypto"
                        if source in [
                            "CoinDesk",
                            "Cointelegraph",
                            "Decrypt",
                            "The Block",
                            "CryptoSlate",
                            "Bitcoin Magazine"
                        ]
                        else "Market"
                    ),

                    "link": item.get(
                        "link",
                        ""
                    ),

                    "id": uid,

                    "date": get_date(item)

                })


        except Exception:

            continue



    # جدیدترین خبرها اول

    news.sort(
        key=lambda x: x["date"],
        reverse=True
    )



    selected = news[:limit]



    # ذخیره خبرهای ارسال شده

    if selected:

        sent.extend(
            [
                x["id"]
                for x in selected
            ]
        )

        save_sent(sent)



    return selected
