import feedparser


SOURCES = {
    "CoinDesk": "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "Cointelegraph": "https://cointelegraph.com/rss",
    "Decrypt": "https://decrypt.co/feed",
    "Bitcoin Magazine": "https://bitcoinmagazine.com/feed",
    "CryptoSlate": "https://cryptoslate.com/feed/"
}


def get_news():

    news_list = []

    for source, url in SOURCES.items():

        try:
            feed = feedparser.parse(url)

            for item in feed.entries[:5]:

                news_list.append({
                    "source": source,
                    "title": item.title,
                    "link": item.link
                })

        except Exception as e:
            print(f"Error from {source}: {e}")

    return news_list


if __name__ == "__main__":

    news = get_news()

    print("Total news:", len(news))

    for n in news:
        print("\n📰", n["source"])
        print(n["title"])
        print(n["link"])
        print("-" * 50)
