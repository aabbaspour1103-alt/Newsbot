import os
import asyncio

from telegram import Bot

from news_scraper import get_news
from translator import translate_text


TOKEN = os.getenv("TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")



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
    link = news["link"]


    translated_title = translate_text(
        title
    )


    message = f"""
📰 خبر جدید کریپتو

🇮🇷 {translated_title}

🌐 منبع:
{source}

🔗 لینک خبر:
{link}

☕ @CryptoBrew
"""


    await bot.send_message(
        chat_id=CHANNEL_ID,
        text=message
    )


    print(
        "✅ خبر با موفقیت ارسال شد"
    )



if __name__ == "__main__":

    asyncio.run(
        send_news()
    )
