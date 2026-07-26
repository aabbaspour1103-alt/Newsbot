import os
import asyncio

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
        "تحلیلگران در حال بررسی پیامدهای احتمالی این خبر هستند."

    ]

    for item in remove_list:

        text = text.replace(
            item,
            ""
        )

    return text.strip()



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
        limit=1
    )



    if not news_list:

        print(
            "❌ خبر جدیدی پیدا نشد"
        )

        return



    news = news_list[0]



    title = news["title"]

    source = news["source"]

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



    translated_title = translate_text(
        title
    )


    translated_description = translate_text(
        description
    )


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

{translated_description}

📰 منبع: {source}

- @CryptoBrew
"""



    await bot.send_message(
        chat_id=CHANNEL_ID,
        text=message.strip()
    )



    print(
        "✅ خبر با موفقیت ارسال شد"
    )



if __name__ == "__main__":

    asyncio.run(
        send_news()
    )
