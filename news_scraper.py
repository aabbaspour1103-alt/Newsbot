import feedparser
import hashlib
import json
import os


NEWS_SOURCES = {

    "CoinDesk": "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "Cointelegraph": "https://cointelegraph.com/rss",
    "Decrypt": "https://decrypt.co/feed",
    "Bloomberg": "https://feeds.bloomberg.com/markets/news.rss",
    "CNBC": "https://www.cnbc.com/id/100003114/device/rss/rss.html",
    "Reuters": "https://feeds.reuters.com/reuters/businessNews"

}


SAVE_FILE = "sent_news.json"



def load_sent():

    if not os.path.exists(SAVE_FILE):
        return []

    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
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
            data,
            f,
            ensure_ascii=False
        )



def news_id(text):

    return hashlib.md5(
        text.encode()
    ).hexdigest()



def get_news(limit=20):

    sent = load_sent()

    news = []


    for source, url in NEWS_SOURCES.items():

        try:

            feed = feedparser.parse(url)


            for item in feed.entries[:5]:

                title = item.get(
                    "title",
                    ""
                )

                link = item.get(
                    "link",
                    ""
                )


                if not title:
                    continue


                uid = news_id(title)


                if uid in sent:
                    continue


                news.append({

                    "source": source,
                    "title": title,
                    "link": link

                })


                sent.append(uid)


                if len(news) >= limit:
                    break


        except Exception:
            continue


    save_sent(sent[-500:])


    return news
