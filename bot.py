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

def clean_text(text, preserve_lines=False):

    if not text:
        return ""

    text = str(text)

    # --------------------------------------------------------
    # HTML
    # --------------------------------------------------------

    text = re.sub(
        r"<[^>]+>",
        " ",
        text
    )

    # --------------------------------------------------------
    # HTML entities
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
    # URL
    # --------------------------------------------------------

    text = re.sub(
        r"https?://\S+",
        " ",
        text
    )

    # --------------------------------------------------------
    # حذف کاراکترهای نامرئی RSS
    # --------------------------------------------------------

    text = re.sub(
        r"[\u200b\u200c\u200d\u200e\u200f\ufeff\u00ad]",
        "",
        text
    )

    # --------------------------------------------------------
    # حذف عبارت‌های مصنوعی
    # --------------------------------------------------------

    remove_list = [

        "این خبر می‌تواند روی روند بازارهای مالی و رفتار سرمایه‌گذاران تاثیرگذار باشد.",
        "این خبر می‌تواند بر روند بازارهای مالی و رفتار سرمایه‌گذاران تأثیرگذار باشد.",
        "این خبر می تواند روی روند بازارهای مالی تاثیرگذار باشد.",
        "این خبر می تواند بر روند بازارهای مالی و رفتار سرمایه گذاران تاثیرگذار باشد.",
        "تحلیلگران در حال بررسی پیامدهای احتمالی این خبر هستند.",

        "undefined",
        "ZZTERM",
        "XQTERM",
        "XQDATE",

        "Click here",
        "Read more",
        "Continue reading",
        "This article",
        "This post",

        "Edge",
        "edge",
    ]

    for item in remove_list:

        text = text.replace(
            item,
            ""
        )

    # --------------------------------------------------------
    # حذف بخش‌های تبلیغاتی Bloomberg و RSS
    # --------------------------------------------------------

    promotional_patterns = [

        r"Opening Trade.*",
        r"افتتاحیه.*",
        r"تجارت افتتاحیه.*",

        r"همه چیزهایی را دارد که شما باید بدانید.*",
        r"همه چیزهایی که شما باید بدانید.*",

        r"Everything you need to know.*",
        r"Everything You Need to Know.*",

        r"با تجزیه و تحلیلی که در هیچ جای دیگری پیدا نخواهید کرد.*",
        r"با تحلیلی که در هیچ جای دیگری پیدا نخواهید کرد.*",

        r"With analysis you won't find anywhere else.*",
        r"With analysis you will not find anywhere else.*",

        r"مجری گری.*",
        r"میزبانی.*",
        r"Hosted by.*",
        r"Host.*",

        r"مهمانان برتر.*",
        r"با مهمانان.*",
        r"پوستی در بازی دارند.*",

    ]

    for pattern in promotional_patterns:

        text = re.sub(
            pattern,
            "",
            text,
            flags=re.IGNORECASE
        )

    # --------------------------------------------------------
    # جداکننده‌های RSS
    # --------------------------------------------------------

    text = re.sub(
        r"\s*\|\s*",
        " ",
        text
    )

    # --------------------------------------------------------
    # فاصله‌ها
    # --------------------------------------------------------

    if preserve_lines:

        text = re.sub(
            r"[ \t]+",
            " ",
            text
        )

        text = re.sub(
            r"\n[ \t]+",
            "\n",
            text
        )

        text = re.sub(
            r"\n\s*\n\s*\n+",
            "\n\n",
            text
        )

    else:

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
    # کلمات تبلیغاتی باقی‌مانده
    # --------------------------------------------------------

    text = re.sub(
        r"\b(?:Click|Read|Continue|Subscribe|Watch)\b",
        "",
        text,
        flags=re.IGNORECASE
    )

    # --------------------------------------------------------
    # حذف تکرار پشت سر هم
    # --------------------------------------------------------

    if not preserve_lines:

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

    # --------------------------------------------------------
    # فاصله اضافی ابتدا و انتها
    # --------------------------------------------------------

    return text.strip()


# ============================================================
# Clean title
# ============================================================

def clean_title(title):

    title = clean_text(
        title
    )

    if not title:
        return ""

    # --------------------------------------------------------
    # حذف جداکننده انتهایی
    # --------------------------------------------------------

    title = re.sub(
        r"\s*[\|\-–—:]+\s*$",
        "",
        title
    )

    # --------------------------------------------------------
    # حذف زباله RSS در انتهای عنوان
    #
    # فقط اگر «را» / «که» / «و» بعد از جداکننده آمده باشد.
    # --------------------------------------------------------

    title = re.sub(
        r"\s*[\|\-–—:]+\s*(?:را|که|و)\s*$",
        "",
        title,
        flags=re.IGNORECASE
    )

    # --------------------------------------------------------
    # حذف «را» تنها در صورتی که کاملاً جدا و در انتها باشد
    #
    # مثال:
    # "عنوان خبر را"
    #
    # اما:
    # "آرا را به دست آورد"
    # دست‌نخورده می‌ماند.
    # --------------------------------------------------------

    if re.search(
        r"\s+را$",
        title
    ):

        # فقط وقتی عنوان ساختار غیرطبیعی RSS داشته باشد
        # و آخرین کلمه «را» باشد.
        title = re.sub(
            r"\s+را$",
            "",
            title
        )

    # --------------------------------------------------------
    # اصلاح فاصله
    # --------------------------------------------------------

    title = re.sub(
        r"\s+",
        " ",
        title
    )

    return title.strip()


# ============================================================
# Clean description
# ============================================================

def clean_description(description):

    description = clean_text(
        description
    )

    if not description:
        return ""

    # --------------------------------------------------------
    # حذف کاراکترهای نامرئی باقی‌مانده
    # --------------------------------------------------------

    description = re.sub(
        r"[\u200b\u200c\u200d\u200e\u200f\ufeff]",
        "",
        description
    )

    # --------------------------------------------------------
    # حذف جداکننده ابتدا و انتها
    # --------------------------------------------------------

    description = re.sub(
        r"^[\s\|\-–—:]+",
        "",
        description
    )

    description = re.sub(
        r"[\s\|\-–—:]+$",
        "",
        description
    )

    # --------------------------------------------------------
    # اگر کل متن فقط یک کلمه بی‌معنی RSS باشد
    # --------------------------------------------------------

    if re.fullmatch(
        r"(را|که|و|از|به)",
        description,
        flags=re.IGNORECASE
    ):

        return ""

    # --------------------------------------------------------
    # حذف «را» خراب در انتهای description
    #
    # فقط وقتی «را» آخرین کلمه است.
    #
    # مثال:
    # "... آرا را"
    #
    # حذف می‌شود.
    #
    # اما:
    # "... آرا را به دست آورد"
    #
    # دست‌نخورده می‌ماند.
    # --------------------------------------------------------

    description = re.sub(
        r"\s+را$",
        "",
        description
    )

    # --------------------------------------------------------
    # حذف «که» یا «و» باقی‌مانده در انتها
    # --------------------------------------------------------

    description = re.sub(
        r"\s+(?:که|و)$",
        "",
        description
    )

    # --------------------------------------------------------
    # اصلاح فاصله
    # --------------------------------------------------------

    description = re.sub(
        r"\s+",
        " ",
        description
    )

    return description.strip()


# ============================================================
# Validate news
# ============================================================

def valid_news(news):

    if not news:
        return False

    title = clean_title(
        news.get(
            "title",
            ""
        )
    )

    description = clean_description(
        news.get(
            "description",
            ""
        )
    )

    if len(title) < 15:
        return False

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

    bad_words = [

        "undefined",
        "None",
        "ZZTERM",
        "XQTERM",
        "XQDATE",

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

        "This article",
        "This post",

    ]

    lowered = text.lower()

    for word in bad_words:

        if word.lower() in lowered:

            score -= 40

    # --------------------------------------------------------
    # ترجمه تقریباً برابر متن انگلیسی
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

            english_chars = len(
                re.findall(
                    r"[A-Za-z]",
                    text
                )
            )

            persian_chars = len(
                re.findall(
                    r"[\u0600-\u06FF]",
                    text
                )
            )

            if english_chars > persian_chars:

                return 0

    # --------------------------------------------------------
    # بررسی فارسی
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
    # تعداد کلمات
    # --------------------------------------------------------

    word_count = len(
        text.split()
    )

    if word_count < 3:

        score -= 40

    elif word_count < 5:

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

    original_title = clean_title(
        news.get(
            "title",
            ""
        )
    )

    original_description = clean_description(
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

    # --------------------------------------------------------
    # پاک‌سازی ترجمه
    # --------------------------------------------------------

    translated_title = clean_title(
        translated_title
    )

    translated_description = clean_description(
        translated_description
    )

    # --------------------------------------------------------
    # امتیاز عنوان
    # --------------------------------------------------------

    title_score = translation_quality(
        translated_title,
        original_title
    )

    # --------------------------------------------------------
    # امتیاز توضیحات
    # --------------------------------------------------------

    if original_description:

        description_score = translation_quality(
            translated_description,
            original_description
        )

    else:

        description_score = 100

    # --------------------------------------------------------
    # امتیاز کلی ترجمه
    # --------------------------------------------------------

    if original_description:

        translation_score = (
            title_score * 0.55
            + description_score * 0.45
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
        "title_translation_score"
    ] = round(
        title_score,
        2
    )

    translated[
        "description_translation_score"
    ] = round(
        description_score,
        2
    )

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

    # فقط 5 خبر برتر ترجمه شوند
    candidates = ranked_news[:5]

    translated_candidates = []

    for news in candidates:

        if not valid_news(news):
            continue

        translated = translate_news(
            news
        )

        title_score = translated.get(
            "title_translation_score",
            0
        )

        description_score = translated.get(
            "description_translation_score",
            0
        )

        translation_score = translated.get(
            "translation_score",
            0
        )

        translated_title = translated.get(
            "translated_title",
            ""
        )

        # ----------------------------------------------------
        # عنوان خراب
        # ----------------------------------------------------

        if not translated_title:

            print(
                "⚠️ عنوان ترجمه نشد؛ خبر رد شد:",
                news.get(
                    "title",
                    ""
                )
            )

            continue

        if title_score < 60:

            print(
                "⚠️ کیفیت عنوان پایین؛ خبر رد شد:",
                news.get(
                    "title",
                    ""
                ),
                "امتیاز:",
                title_score
            )

            continue

        # ----------------------------------------------------
        # توضیح ضعیف
        # ----------------------------------------------------

        if (
            news.get(
                "description",
                ""
            )
            and description_score < 45
        ):

            print(
                "⚠️ توضیحات ترجمه ضعیف است؛ توضیحات حذف شد:",
                news.get(
                    "title",
                    ""
                ),
                "امتیاز:",
                description_score
            )

            translated[
                "translated_description"
            ] = ""

            translated[
                "translation_score"
            ] = round(
                title_score,
                2
            )

            translation_score = title_score

        # ----------------------------------------------------
        # کیفیت کلی
        # ----------------------------------------------------

        if translation_score < 55:

            print(
                "⚠️ کیفیت کلی ترجمه پایین؛ خبر رد شد:",
                news.get(
                    "title",
                    ""
                ),
                "امتیاز:",
                translation_score
            )

            continue

        translated_candidates.append(
            translated
        )

    if not translated_candidates:
        return None

    # --------------------------------------------------------
    # امتیاز نهایی
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
    # انتخاب یک خبر
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
            str(
                x.get(
                    "date",
                    ""
                )
            )
        ),
        reverse=True
    )

    return translated_candidates[0]


# ============================================================
# Build Telegram message
# ============================================================

def build_message(news):

    title = clean_title(
        news.get(
            "translated_title",
            ""
        )
    )

    description = clean_description(
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
    # Header
    # --------------------------------------------------------

    if urgent:

        header = "🚨 خـــبر فـــوری"

    else:

        header = "📰 اخبــار بـازار"

    # --------------------------------------------------------
    # عنوان الزامی
    # --------------------------------------------------------

    if not title:
        return ""

    # --------------------------------------------------------
    # ساخت پیام
    # --------------------------------------------------------

    parts = [

        header,

        "",

        f"🔹 {title}",

    ]

    # --------------------------------------------------------
    # توضیحات
    # --------------------------------------------------------

    if description:

        parts.extend([
            "",
            description,
        ])

    # --------------------------------------------------------
    # منبع
    # --------------------------------------------------------

    parts.extend([

        "",

        f"📰 منبع: {source}",

        "@CryptoBrew",

    ])

    # --------------------------------------------------------
    # ساخت نهایی
    # --------------------------------------------------------

    message = "\n".join(
        parts
    )

    # --------------------------------------------------------
    # پاک‌سازی نهایی
    # --------------------------------------------------------

    message = clean_text(
        message,
        preserve_lines=True
    )

    # --------------------------------------------------------
    # اطمینان از فاصله بین منبع و آیدی کانال
    # --------------------------------------------------------

    message = re.sub(
        r"(📰 منبع:[^\n]+)\s+(@CryptoBrew)",
        r"\1\n\2",
        message
    )

    return message.strip()


# ============================================================
# Send news
# ============================================================

async def send_news():

    # --------------------------------------------------------
    # TOKEN
    # --------------------------------------------------------

    if not TOKEN:

        print(
            "❌ TOKEN پیدا نشد"
        )

        return

    # --------------------------------------------------------
    # CHANNEL_ID
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
        # انتخاب بهترین خبر
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
        # اطلاعات خبر
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
            "📝 امتیاز عنوان:",
            news.get(
                "title_translation_score",
                0
            )
        )

        print(
            "📄 امتیاز توضیحات:",
            news.get(
                "description_translation_score",
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

        # ----------------------------------------------------
        # عنوان ترجمه‌شده
        # ----------------------------------------------------

        if not news.get(
            "translated_title",
            ""
        ).strip():

            print(
                "❌ عنوان ترجمه‌شده وجود ندارد"
            )

            return

        # ====================================================
        # ارسال
        # ====================================================

        await bot.send_message(
            chat_id=CHANNEL_ID,
            text=message
        )

        # ====================================================
        # ثبت بعد از ارسال موفق
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
