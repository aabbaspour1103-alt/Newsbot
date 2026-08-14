import os
import asyncio
import re

from telegram import Bot

from news_scraper import (
    get_news,
    mark_as_sent
)

from news_filter import (
    rank_news
)

from translator import (
    translate_text
)


TOKEN = os.getenv("TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")


# ============================================================
# Text cleaning
# ============================================================

def clean_text(text):

    if not text:
        return ""

    remove_list = [

        "این خبر می‌تواند روی روند بازارهای مالی و رفتار سرمایه‌گذاران تاثیرگذار باشد.",
        "این خبر می‌تواند بر روند بازارهای مالی و رفتار سرمایه‌گذاران تأثیرگذار باشد.",
        "تحلیلگران در حال بررسی پیامدهای احتمالی این خبر هستند.",
        "این خبر می تواند روی روند بازارهای مالی تاثیرگذار باشد.",

        "Edge",
        "edge",

    ]

    for item in remove_list:

        text = text.replace(
            item,
            ""
        )

    # --------------------------------------------------------
    # حذف تکرار کلمات پشت سر هم
    # --------------------------------------------------------

    words = text.split()

    fixed_words = []

    for word in words:

        if (
            not fixed_words
            or word != fixed_words[-1]
        ):
            fixed_words.append(word)

    text = " ".join(
        fixed_words
    )

    # --------------------------------------------------------
    # حذف HTML entity
    # --------------------------------------------------------

    text = text.replace(
        "&#160;",
        " "
    )

    text = text.replace(
        "&nbsp;",
        " "
    )

    # --------------------------------------------------------
    # حذف فاصله‌های اضافی
    # --------------------------------------------------------

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    # --------------------------------------------------------
    # فاصله قبل از علائم
    # --------------------------------------------------------

    text = re.sub(
        r"\s+،",
        "،",
        text
    )

    text = re.sub(
        r"\s+\.",
        ".",
        text
    )

    text = re.sub(
        r"\s+؟",
        "؟",
        text
    )

    return text.strip()


# ============================================================
# Validate news
# ============================================================

def valid_news(news):

    if not news:
        return False

    title = news.get(
        "title",
        ""
    ).strip()

    description = news.get(
        "description",
        ""
    ).strip()

    if len(title) < 15:
        return False

    # خبر باید حداقل عنوان داشته باشد.
    # توضیح خالی باعث حذف کامل خبر نمی‌شود،
    # چون بعضی منابع RSS توضیح ندارند.

    if len(description) > 3000:
        return False

    return True


# ============================================================
# Translation quality
# ============================================================

def translation_quality(
    translated,
    original=""
):

    if not translated:
        return 0

    text = translated.strip()

    if not text:
        return 0

    score = 100

    bad_words = [

        "undefined",
        "None",
        "ZZTERM",

        "Edge",
        "edge",

        "بهره بهره",
        "سوار شد",

        "Reg کریپتو",
        "Reg crypto",

        "Click here",
        "Read more",
        "Continue reading",

    ]

    for word in bad_words:

        if word.lower() in text.lower():

            score -= 40

    # --------------------------------------------------------
    # فارسی بودن متن
    # --------------------------------------------------------

    persian_chars = len(
        re.findall(
            r"[\u0600-\u06FF]",
            text
        )
    )

    english_chars = len(
        re.findall(
            r"[A-Za-z]",
            text
        )
    )

    if len(text) >= 50:

        if persian_chars == 0:
            score -= 50

        elif english_chars > persian_chars * 2:
            score -= 30

    # --------------------------------------------------------
    # متن خیلی کوتاه
    # --------------------------------------------------------

    if len(text) < 20:
        score -= 30

    elif len(text) < 50:
        score -= 10

    # --------------------------------------------------------
    # جمله ناقص
    # --------------------------------------------------------

    if text.endswith(
        "..."
    ):
        score -= 5

    return max(
        0,
        score
    )


# ============================================================
# Translate news
# ============================================================

def translate_news(news):

    original_title = news.get(
        "title",
        ""
    )

    original_description = news.get(
        "description",
        ""
    )

    try:

        translated_title = translate_text(
            original_title
        )

    except Exception as e:

        print(
            "خطا در ترجمه عنوان:",
            e
        )

        translated_title = original_title

    try:

        translated_description = translate_text(
            original_description
        )

    except Exception as e:

        print(
            "خطا در ترجمه توضیحات:",
            e
        )

        translated_description = original_description

    translated_title = clean_text(
        translated_title
    )

    translated_description = clean_text(
        translated_description
    )

    title_score = translation_quality(
        translated_title,
        original_title
    )

    description_score = translation_quality(
        translated_description,
        original_description
    )

    # اگر توضیح وجود ندارد، کیفیت عنوان مهم‌تر است.
    if original_description:

        translation_score = (
            title_score * 0.45
            + description_score * 0.55
        )

    else:

        translation_score = title_score

    translated = dict(
        news
    )

    translated[
        "translated_title"
    ] = translated_title

    translated[
        "translated_description"
    ] = translated_description

    translated[
        "translation_score"
    ] = round(
        translation_score,
        2
    )

    return translated


# ============================================================
# Select best translated news
# ============================================================

def select_best_translated_news(
    ranked_news
):

    if not ranked_news:
        return None

    # --------------------------------------------------------
    # فقط چند کاندید برتر ترجمه می‌شوند.
    #
    # این کار باعث می‌شود برای 30 خبر، 60 درخواست ترجمه
    # ارسال نشود.
    # --------------------------------------------------------

    candidates = ranked_news[:5]

    translated_candidates = []

    for news in candidates:

        if not valid_news(news):
            continue

        translated = translate_news(
            news
        )

        translated_candidates.append(
            translated
        )

    if not translated_candidates:
        return None

    # --------------------------------------------------------
    # امتیاز نهایی:
    #
    # امتیاز خبر      70%
    # کیفیت ترجمه     30%
    # --------------------------------------------------------

    for item in translated_candidates:

        news_score = item.get(
            "score",
            0
        )

        translation_score = item.get(
            "translation_score",
            0
        )

        item[
            "final_score"
        ] = round(
            news_score * 0.70
            + translation_score * 0.30,
            2
        )

    translated_candidates.sort(
        key=lambda x: (
            x.get(
                "final_score",
                0
            ),
            x.get(
                "score",
                0
            )
        ),
        reverse=True
    )

    return translated_candidates[0]


# ============================================================
# Build Telegram message
# ============================================================

def build_message(news):

    title = clean_text(
        news.get(
            "translated_title",
            news.get(
                "title",
                ""
            )
        )
    )

    description = clean_text(
        news.get(
            "translated_description",
            news.get(
                "description",
                ""
            )
        )
    )

    source = news.get(
        "source",
        "Unknown"
    )

    urgent = news.get(
        "urgent",
        False
    )

    # --------------------------------------------------------
    # خبر فوری اولویت دارد
    # --------------------------------------------------------

    if urgent:

        header = "🚨 خـــبر فـــوری"

    else:

        header = "📰 اخبــار بـازار"

    # --------------------------------------------------------
    # پیام
    # --------------------------------------------------------

    message = (
        f"{header}\n\n"
        f"🔹 {title}"
    )

    if description:

        message += (
            f"\n\n"
            f"{description}"
        )

    message += (
        f"\n\n"
        f"📰 منبع: {source}"
        f"\n"
        f"@CryptoBrew"
    )

    return message.strip()


# ============================================================
# Send news
# ============================================================

async def send_news():

    if not TOKEN:

        print(
            "❌ TOKEN پیدا نشد"
        )

        return

    if not CHANNEL_ID:

        print(
            "❌ CHANNEL_ID پیدا نشد"
        )

        return

    bot = Bot(
        token=TOKEN
    )

    try:

        # ----------------------------------------------------
        # دریافت اخبار جدید
        # ----------------------------------------------------

        news_list = get_news(
            limit=30
        )

        if not news_list:

            print(
                "❌ خبر جدیدی پیدا نشد"
            )

            return

        print(
            f"📰 تعداد اخبار دریافت‌شده: {len(news_list)}"
        )

        # ----------------------------------------------------
        # رتبه‌بندی اخبار
        # ----------------------------------------------------

        ranked_news = rank_news(
            news_list
        )

        if not ranked_news:

            print(
                "❌ خبر مناسبی پیدا نشد"
            )

            return

        # ----------------------------------------------------
        # انتخاب بهترین خبر پس از ترجمه
        # ----------------------------------------------------

        news = select_best_translated_news(
            ranked_news
        )

        if not news:

            print(
                "❌ هیچ خبر قابل‌انتشاری پیدا نشد"
            )

            return

        print(
            "🏆 خبر انتخاب‌شده:"
        )

        print(
            news.get(
                "title",
                ""
            )
        )

        print(
            "📊 امتیاز خبر:",
            news.get(
                "score",
                0
            )
        )

        print(
            "🌐 امتیاز ترجمه:",
            news.get(
                "translation_score",
                0
            )
        )

        print(
            "⭐ امتیاز نهایی:",
            news.get(
                "final_score",
                0
            )
        )

        # ----------------------------------------------------
        # ساخت پیام
        # ----------------------------------------------------

        message = build_message(
            news
        )

        # ----------------------------------------------------
        # ارسال
        # ----------------------------------------------------

        await bot.send_message(
            chat_id=CHANNEL_ID,
            text=message
        )

        # ----------------------------------------------------
        # فقط بعد از ارسال موفق ثبت شود
        # ----------------------------------------------------

        mark_as_sent(
            news
        )

        print(
            "✅ خبر با موفقیت ارسال و ثبت شد"
        )

    except Exception as e:

        print(
            f"❌ خطا در ارسال خبر: {e}"
        )


# ============================================================
# Run
# ============================================================

if __name__ == "__main__":

    asyncio.run(
        send_news()
    )
