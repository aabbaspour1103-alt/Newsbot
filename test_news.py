from news_scraper import get_news


news = get_news()


for item in news:
    print("📰 منبع:", item["source"])
    print("عنوان:", item["title"])
    print("لینک:", item["link"])
    print("-" * 60)
