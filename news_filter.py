import json
import os


DATABASE_FILE = "sent_news.json"


def load_sent_news():

    if not os.path.exists(DATABASE_FILE):
        return []

    with open(DATABASE_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_sent_news(news):

    with open(DATABASE_FILE, "w", encoding="utf-8") as file:
        json.dump(
            news,
            file,
            ensure_ascii=False,
            indent=4
        )


def is_new_news(link):

    sent_news = load_sent_news()

    if link in sent_news:
        return False

    sent_news.append(link)

    # نگهداری آخرین 200 خبر
    sent_news = sent_news[-200:]

    save_sent_news(sent_news)

    return True


if __name__ == "__main__":

    test_link = "https://example.com/news1"

    if is_new_news(test_link):
        print("خبر جدید است ✅")
    else:
        print("خبر تکراری است ❌")
