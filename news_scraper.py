import feedparser


SOURCES = {
    "CoinDesk": "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "Cointelegraph": "https://cointelegraph.com/rss"
}


def get_news():

    news_list = []

    for source, url in SOURCES.items():

        feed = feedparser.parse(url)

        for item in feed.entries[:5]:

            news_list.append({
                "source": source,
                "title": item.title,
                "link": item.link
            })

    return news_list


if __name__ == "__main__":

    news = get_news()

    for n in news:
        print("📰", n["source"])
        print(n["title"])
        print(n["link"])
        print("-" * 50)
