from news_scraper import get_news
from translator import translate_text
from news_filter import is_new_news


news = get_news()

print("تعداد خبرهای دریافت شده:", len(news))


for item in news:

    if is_new_news(item["link"]):

        translated_title = translate_text(item["title"])

        print("\n🆕 خبر جدید")
        print("📰 منبع:", item["source"])
        print("🇮🇷 ترجمه:")
        print(translated_title)
        print("🔗 لینک:")
        print(item["link"])

        print("-" * 60)

    else:
        print("⏭ خبر تکراری حذف شد:")
        print(item["title"])
