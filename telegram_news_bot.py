import os
from telegram import Bot

from news_scraper import get_news
from translator import translate_text


TOKEN = os.getenv("TOKEN")

CHANNEL_ID = "@CryptoBrew"



def format_news(news):

    title = translate_text(
        news["title"]
    )


    message = f"""
📰 خبر جدید کریپتو

🇮🇷 {title}

🌐 منبع:
{news["source"]}

🔗 لینک خبر:
{news["link"]}

⏰ CryptoBrew
"""


    return message.strip()



def send_news():

    if not TOKEN:

        print(
            "خطا: TOKEN تنظیم نشده است"
        )

        return


    bot = Bot(
        token=TOKEN
    )


    news_list = get_news(
        limit=5
    )


    if not news_list:

        print(
            "خبر جدیدی وجود ندارد"
        )

        return



    for news in news_list:


        message = format_news(
            news
        )


        try:

            bot.send_message(
                chat_id=CHANNEL_ID,
                text=message
            )


            print(
                "ارسال شد:",
                news["title"]
            )


        except Exception as e:

            print(
                "خطا در ارسال:",
                e
            )



if __name__ == "__main__":

    send_news()
