import os
import asyncio
import re

from telegram import Bot

from news_scraper import get_news
from translator import translate_text


TOKEN = os.getenv("TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")


def clean_text(text):

    if not text:
        return ""

    remove_list = [

        "این خبر می‌تواند روی روند بازارهای مالی و رفتار سرمایه‌گذاران تاثیرگذار باشد.",
        "تحلیلگران در حال بررسی پیامدهای احتمالی این خبر هستند.",
        "این خبر می تواند روی روند بازارهای مالی تاثیرگذار باشد.",
        "Edge",
        "edge"

    ]

    for item in remove_list:
        text = text.replace(item, "")


    # حذف کلمات تکراری پشت سر هم
    words = text.split()

    fixed_words = []

    for word in words:

        if not fixed_words or word != fixed_words[-1]:
            fixed_words.append(word)


    text = " ".join(fixed_words)


    # حذف حروف انگلیسی چسبیده به فارسی
    text = re.sub(
        r"([آ-ی])([a-zA-Z]+)",
        r"\1",
        text
    )


    # حذف فاصله های اضافی
    text = re.sub(
        r"\s+",
        " ",
        text
    )


    return text.strip()



def valid_news(news):

    if not news:
        return False


    title = news.get(
        "title",
        ""
    ).strip()


    if len(title) < 15:
        return False


    return True



def bad_translation(text):

    if not text:
        return True


    bad_words = [

        "بهره بهره",
        "Edge",
        "edge",
        "undefined",
        "None"

    ]


    for word in bad_words:

        if word in text:
            return True


    return False



async def send_news():

    if not TOKEN:

        print("❌ TOKEN پیدا نشد")
        return


    if not CHANNEL_ID:

        print("❌ CHANNEL_ID پیدا نشد")
        return



    bot = Bot(
        token=TOKEN
    )


    news_list = get_news(
        limit=10
    )


    if not news_list:

        print("❌ خبر جدیدی پیدا نشد")
        return



    news = None


    for item in news_list:

        if valid_news(item):

            news = item
            break



    if not news:

        print("❌ خبر معتبر پیدا نشد")
        return



    title = news.get(
        "title",
        ""
    )


    source = news.get(
        "source",
        "Unknown"
    )


    category = news.get(
        "category",
        "Market"
    )


    description = news.get(
        "description",
        ""
    )


    urgent = news.get(
        "urgent",
        False
    )



    try:

        translated_title = translate_text(
            title
        )

    except Exception:

        translated_title = title



    translated_title = clean_text(
        translated_title
    )



    # اگر ترجمه خراب بود، متن اصلی را استفاده کن
    if bad_translation(translated_title):

        translated_title = title



    try:

        translated_description = translate_text(
            description
        )

    except Exception:

        translated_description = description



    translated_description = clean_text(
        translated_description
    )



    if category == "Crypto":

        header = "📰 اخبــار بـازار"

    elif urgent:

        header = "🚨 خـــبر فـــوری"

    else:

        header = "🚨 خـــبر"



    message = f"""
{header}

- {translated_title}
"""


    if translated_description:

        message += f"""

{translated_description}
"""


    message += f"""

📰 منبع: {source}

- @CryptoBrew
"""



    try:

        await bot.send_message(
            chat_id=CHANNEL_ID,
            text=message.strip()
        )


        print(
            "✅ خبر با موفقیت ارسال شد"
        )


    except Exception as e:

        print(
            f"❌ خطا در ارسال تلگرام: {e}"
        )



if __name__ == "__main__":

    asyncio.run(
        send_news()
    )
