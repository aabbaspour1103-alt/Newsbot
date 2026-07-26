import feedparser
import hashlib
import json
import os
import re


NEWS_SOURCES = {

    # Crypto
    "CoinDesk": "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "Cointelegraph": "https://cointelegraph.com/rss",
    "Decrypt": "https://decrypt.co/feed",
    "The Block": "https://www.theblock.co/rss.xml",
    "CryptoSlate": "https://cryptoslate.com/feed/",
    "Bitcoin Magazine": "https://bitcoinmagazine.com/.rss/full/",

    # Markets
    "Bloomberg": "https://feeds.bloomberg.com/markets/news.rss",
    "CNBC": "https://www.cnbc.com/id/100003114/device/rss/rss.html",
    "Reuters": "https://feeds.reuters.com/reuters/businessNews",

}


SAVE_FILE = "sent_news.json"


URGENT_WORDS = [

    "Trump",
    "Donald Trump",
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
    "emergency",
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



def shorten(text, limit=250):

    if len(text) <= limit:
        return text

    return text[:limit] + "..."



def news_id(text):

    return hashlib.md5(
        text.encode("utf-8")
    ).hexdigest()



def check_priority(text):

    text = text.lower()

    for word in URGENT_WORDS:

        if word.lower() in text:
            return "urgent"

    return "normal"



def get_news(limit=10):

    sent = load_sent()

    news = []


    for source, url in NEWS_SOURCES.items():

        try:

            feed = feedparser.parse(url)


            for item in feed.entries[:10]:

                title = clean_text(
                    item.get(
                        "title",
                        ""
                    )
                )


                if not title:
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


                description = shorten(
                    description
                )


                uid = news_id(
                    title
                )


                if uid in sent:
                    continue


                priority = check_priority(
                    title + " " + description
                )


                news.append({

                    "source": source,

                    "title": title,

                    "description": description,

                    "priority": priority,

                    "link": item.get(
                        "link",
                        ""
                    )

                })


                sent.append(uid)


                if len(news) >= limit:
                    break


            if len(news) >= limit:
                break


        except Exception:

            continue



    save_sent(sent)


    return news
