from news_scraper import get_news
from translator import translate_text


news = get_news()


print("تعداد خبرها:", len(news))


for item in news:

    translated_title = translate_text(item["title"])

    print("\n📰 منبع:", item["source"])
    print("🇬🇧 عنوان اصلی:")
    print(item["title"])

    print("🇮🇷 ترجمه:")
    print(translated_title)

    print("🔗 لینک:")
    print(item["link"])

    print("-" * 60)
