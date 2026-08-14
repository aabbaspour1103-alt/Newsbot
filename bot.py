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

    text = str(text)

    # --------------------------------------------------------
    # حذف عبارت‌های اضافی و مصنوعی
    # --------------------------------------------------------

    remove_list = [

        "این خبر می‌تواند روی روند بازارهای مالی و رفتار سرمایه‌گذاران تاثیرگذار باشد.",
        "این خبر می‌تواند بر روند بازارهای مالی و رفتار سرمایه‌گذاران تأثیرگذار باشد.",
        "این خبر می تواند روی روند بازارهای مالی تاثیرگذار باشد.",
        "این خبر می تواند بر روند بازارهای مالی و رفتار سرمایه گذاران تاثیرگذار باشد.",
        "تحلیلگران در حال بررسی پیامدهای احتمالی این خبر هستند.",

        "Edge",
        "edge",

    ]

    for item in remove_list:

        text = text.replace(
            item,
            ""
        )

    # --------------------------------------------------------
    # حذف HTML
    # --------------------------------------------------------

    text = re.sub(
        r"<[^>]+>",
        " ",
        text
    )

    # --------------------------------------------------------
    # حذف entity
    # --------------------------------------------------------

    text = re.sub(
        r"&(?:nbsp|#160);",
        " ",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"&[a-zA-Z0-9#]+;",
        " ",
        text
    )

    # --------------------------------------------------------
    # حذف URL
    # --------------------------------------------------------

    text = re.sub(
        r"https?://\S+",
        " ",
        text
    )

    # --------------------------------------------------------
    # فاصله‌های اضافی
    # --------------------------------------------------------

    text = re.sub(
        r"[\r\n\t]+",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    # --------------------------------------------------------
    # حذف کلمات تکراری پشت سر هم
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
    # اصلاح فاصله قبل از علائم
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
        r"\s+؛",
        "؛",
        text
    )

    text = re.sub(
        r"\s+؟",
        "؟",
        text
    )

    text = re.sub(
        r"\s+!",
        "!",
        text
    )

    text = re.sub(
        r"\s+٪",
        "٪",
        text
    )

    return text.strip()


# ============================================================
# Validate news
# ============================================================

def valid_news(news):

    if not news:
        return False

    title = clean_text(
        news.get(
            "title",
            ""
        )
    )

    description = clean_text(
        news.get(
            "description",
            ""
        )
    )

    # عنوان خیلی کوتاه نباشد
    if len(title) < 15:
        return False

    # متن غیرعادی بزرگ نباشد
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

    text = clean_text(
        translated
    )

    if not text:
        return 0

    score = 100

    # --------------------------------------------------------
    # عبارت‌های خراب
    # --------------------------------------------------------

    bad_words = [

        "undefined",
        "None",
        "ZZTERM",

        "سوار شد",

        "بهره بهره",
        "بازده بازده",
        "سهام سهام",

        "Reg کریپتو",
        "Reg crypto",

        "در به عنوان",

        "شما و",
        "اول است",

        "Click here",
        "Read more",
        "Continue reading",

    ]

    lowered = text.lower()

    for word in bad_words:

        if word.lower() in lowered:

            score -= 40

    # --------------------------------------------------------
    # اگر متن انگلیسی اصلی را تقریباً دست‌نخورده برگرداند
    # --------------------------------------------------------

    if original:

        original_clean = clean_text(
            original
        ).lower()

        translated_clean = text.lower()

        if (
            len(original_clean) > 30
            and translated_clean == original_clean
        ):
            return 0

    # --------------------------------------------------------
    # بررسی فارسی بودن
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

    if len(text) >= 30:

        if persian_chars == 0:

            score -= 60

        elif english_chars > persian_chars * 2:

            score -= 35

    # --------------------------------------------------------
    # متن خیلی کوتاه
    # --------------------------------------------------------

    word_count = len(
        text.split()
    )

    if word_count < 4:

        score -= 40

    elif word_count < 6:

        score -= 15

    # --------------------------------------------------------
    # متن ناقص
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

    original_title = clean_text(
        news.get(
            "title",
            ""
        )
    )

    original_description = clean_text(
        news.get(
            "description",
            ""
        )
    )

    # --------------------------------------------------------
    # ترجمه عنوان
    # --------------------------------------------------------

    try:

        translated_title = translate_text(
            original_title
        )

    except Exception as e:

        print(
            "❌ خطا در ترجمه عنوان:",
            e
        )

        translated_title = ""

    # --------------------------------------------------------
    # ترجمه توضیحات
    # --------------------------------------------------------

    try:

        translated_description = translate_text(
            original_description
        )

    except Exception as e:

        print(
            "❌ خطا در ترجمه توضیحات:",
            e
        )

        translated_description = ""

    translated_title = clean_text(
        translated_title
    )

    translated_description = clean_text(
        translated_description
    )

    # --------------------------------------------------------
    # امتیاز ترجمه
    # --------------------------------------------------------

    title_score = translation_quality(
        translated_title,
        original_title
    )

    description_score = translation_quality(
        translated_description,
        original_description
    )

    # اگر توضیح وجود داشته باشد،
    # عنوان و توضیح هر دو اهمیت دارند.

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
    # فقط 5 خبر برتر را ترجمه می‌کنیم
    # --------------------------------------------------------

    candidates = ranked_news[:5]

    translated_candidates = []

    for news in candidates:

        if not valid_news(news):
            continue

        translated = translate_news(
            news
        )

        translation_score = translated.get(
            "translation_score",
            0
        )

        # ----------------------------------------------------
        # ترجمه خیلی ضعیف نباید منتشر شود
        # ----------------------------------------------------

        if translation_score < 55:

            print(
                "⚠️ ترجمه ضعیف؛ خبر رد شد:",
                news.get(
                    "title",
                    ""
                ),
                "امتیاز:",
                translation_score
            )

            continue

        # عنوان ترجمه‌شده حتماً باید وجود داشته باشد
        if not translated.get(
            "translated_title"
        ):
            continue

        translated_candidates.append(
            translated
        )

    if not translated_candidates:

        return None

    # --------------------------------------------------------
    # امتیاز نهایی
    #
    # اهمیت خبر       65%
    # کیفیت ترجمه     35%
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
            news_score * 0.65
            + translation_score * 0.35,
            2
        )

    # --------------------------------------------------------
    # انتخاب فقط یک خبر
    # --------------------------------------------------------

    translated_candidates.sort(
        key=lambda x: (
            x.get(
                "final_score",
                0
            ),
            x.get(
                "score",
                0
            ),
            x.get(
                "date"
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
            ""
        )
    )

    description = clean_text(
        news.get(
            "translated_description",
            ""
        )
    )

    source = clean_text(
        news.get(
            "source",
            "Unknown"
        )
    )

    urgent = news.get(
        "urgent",
        False
    )

    # --------------------------------------------------------
    # عنوان
    # --------------------------------------------------------

    if urgent:

        header = "🚨 خـــبر فـــوری"

    else:

        header = "📰 اخبــار بـازار"

    # --------------------------------------------------------
    # ساخت پیام
    # --------------------------------------------------------

    parts = [

        header,

        "",

        f"🔹 {title}",

    ]

    if description:

        parts.extend([
            "",
            description,
        ])

    parts.extend([
        "",
        f"📰 منبع: {source}",
        "@CryptoBrew",
    ])

    message = "\n".join(
        parts
    )

    return clean_text(
        message
    )


# ============================================================
# Send news
# ============================================================

async def send_news():

    # --------------------------------------------------------
    # بررسی TOKEN
    # --------------------------------------------------------

    if not TOKEN:

        print(
            "❌ TOKEN پیدا نشد"
        )

        return

    # --------------------------------------------------------
    # بررسی CHANNEL_ID
    # --------------------------------------------------------

    if not CHANNEL_ID:

        print(
            "❌ CHANNEL_ID پیدا نشد"
        )

        return

    bot = Bot(
        token=TOKEN
    )

    try:

        # ====================================================
        # دریافت اخبار
        # ====================================================

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

        # ====================================================
        # رتبه‌بندی
        # ====================================================

        ranked_news = rank_news(
            news_list
        )

        if not ranked_news:

            print(
                "❌ خبر مناسبی پیدا نشد"
            )

            return

        print(
            f"🏆 تعداد اخبار رتبه‌بندی‌شده: {len(ranked_news)}"
        )

        # ====================================================
        # انتخاب بهترین خبر بعد از بررسی ترجمه
        # ====================================================

        news = select_best_translated_news(
            ranked_news
        )

        if not news:

            print(
                "❌ هیچ خبر قابل‌انتشاری پیدا نشد"
            )

            return

        # ====================================================
        # اطلاعات خبر انتخاب‌شده
        # ====================================================

        print(
            "\n=============================="
        )

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
            "📰 منبع:",
            news.get(
                "source",
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

        print(
            "==============================\n"
        )

        # ====================================================
        # ساخت پیام
        # ====================================================

        message = build_message(
            news
        )

        if not message:

            print(
                "❌ پیام نهایی خالی است"
            )

            return

        # ====================================================
        # ارسال به تلگرام
        # ====================================================

        await bot.send_message(
            chat_id=CHANNEL_ID,
            text=message
        )

        # ====================================================
        # فقط بعد از ارسال موفق ثبت شود
        # ====================================================

        mark_as_sent(
            news
        )

        print(
            "✅ خبر با موفقیت ارسال شد"
        )

        print(
            "✅ خبر در sent_news.json ثبت شد"
        )

    except Exception as e:

        print(
            "❌ خطا در ارسال خبر:",
            e
        )

    finally:

        try:

            await bot.close()

        except Exception:

            pass


# ============================================================
# Run
# ============================================================

if __name__ == "__main__":

    asyncio.run(
        send_news()
    )
