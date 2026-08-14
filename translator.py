from deep_translator import GoogleTranslator
import re
import html
from datetime import datetime


# ============================================================
# Protected terms
# ============================================================

PROTECTED_TERMS = {

    # --------------------------------------------------------
    # Crypto
    # --------------------------------------------------------

    "Bitcoin Core": "Bitcoin Core",
    "Bitcoin ETF": "ETF بیت‌کوین",
    "Ethereum ETF": "ETF اتریوم",

    "Bitcoin": "بیت‌کوین",
    "Ethereum": "اتریوم",
    "Binance Coin": "بایننس کوین",
    "Binance": "بایننس",
    "Solana": "سولانا",
    "Ripple": "ریپل",
    "Dogecoin": "دوج‌کوین",
    "Shiba Inu": "شیبا اینو",
    "Cardano": "کاردانو",
    "Polygon": "پالیگان",
    "Toncoin": "تون‌کوین",
    "Tether": "تتر",

    "BNB": "BNB",
    "XRP": "XRP",
    "USDT": "USDT",
    "ETF": "ETF",
    "NFT": "NFT",
    "DAO": "DAO",
    "DeFi": "دیفای",
    "Web3": "وب۳",

    "Cryptocurrencies": "ارزهای دیجیتال",
    "Cryptocurrency": "ارز دیجیتال",
    "Crypto": "کریپتو",
    "crypto": "کریپتو",

    "Blockchain": "بلاکچین",
    "blockchain": "بلاکچین",

    "Stablecoins": "استیبل‌کوین‌ها",
    "Stablecoin": "استیبل‌کوین",

    "Tokens": "توکن‌ها",
    "Token": "توکن",

    "Exchange": "صرافی",
    "Exchanges": "صرافی‌ها",

    # --------------------------------------------------------
    # Finance
    # --------------------------------------------------------

    "Federal Reserve": "فدرال رزرو آمریکا",
    "Fed": "فدرال رزرو آمریکا",
    "Jerome Powell": "جروم پاول",

    "Securities and Exchange Commission": (
        "کمیسیون بورس و اوراق بهادار آمریکا (SEC)"
    ),

    "SEC": "کمیسیون بورس و اوراق بهادار آمریکا (SEC)",
    "CFTC": "کمیسیون معاملات آتی کالای آمریکا (CFTC)",

    "interest rates": "نرخ‌های بهره",
    "interest rate": "نرخ بهره",

    "rate hikes": "افزایش نرخ بهره",
    "rate hike": "افزایش نرخ بهره",

    "rate cuts": "کاهش نرخ بهره",
    "rate cut": "کاهش نرخ بهره",

    "inflation": "تورم",
    "recession": "رکود اقتصادی",

    "bond markets": "بازارهای اوراق قرضه",
    "bond market": "بازار اوراق قرضه",

    "bond traders": "معامله‌گران اوراق قرضه",
    "bond yields": "بازده اوراق قرضه",
    "yield": "بازده",

    "stock markets": "بازارهای سهام",
    "stock market": "بازار سهام",

    "market capitalization": "ارزش بازار",

    "net income": "درآمد خالص",
    "annual threshold": "آستانه سالانه",

    "underlying assets": "دارایی‌های پایه",

    "institutional investors": "سرمایه‌گذاران نهادی",
    "investors": "سرمایه‌گذاران",

    "investments": "سرمایه‌گذاری‌ها",
    "investment": "سرمایه‌گذاری",

    "shares": "سهام",
    "share": "سهم",

    "issuer": "ناشر",
    "issuers": "ناشران",

    "provider": "ارائه‌دهنده",
    "providers": "ارائه‌دهندگان",

    "Trust": "تراست",

    # --------------------------------------------------------
    # Companies
    # --------------------------------------------------------

    "Hashdex": "Hashdex",
    "Metaplanet": "متاپلنِت",
    "Trezor": "ترزور",

    # --------------------------------------------------------
    # Security / Regulation
    # --------------------------------------------------------

    "data breach": "نقض امنیت داده",
    "security breach": "نقض امنیتی",

    "hacked": "هک شد",
    "hack": "هک",

    "sanctions": "تحریم‌ها",
    "sanction": "تحریم",

    "breaking news": "خبر فوری",

}


# ============================================================
# Common translation corrections
# ============================================================

REPLACE_WORDS = {

    "Reg کریپتو": "مقررات کریپتو",
    "Reg crypto": "مقررات کریپتو",
    "crypto Reg": "مقررات کریپتو",
    "Crypto Reg": "مقررات کریپتو",

    "ارزهای رمزنگاری شده": "ارزهای دیجیتال",
    "ارز رمزنگاری شده": "ارز دیجیتال",

    "ارز رمزنگاری‌شده": "ارز دیجیتال",
    "ارزهای رمزنگاری‌شده": "ارزهای دیجیتال",

    "رمزنگاری": "کریپتو",

    "بهره بهره": "بهره",
    "بازده بازده": "بازده",
    "سهام سهام": "سهام",

    "اوراق قرضههای": "اوراق قرضه",
    "اوراق قرضه های": "اوراق قرضه",

    "ارائه دهنده": "ارائه‌دهنده",
    "ارائه دهندگان": "ارائه‌دهندگان",

    "سرمایه گذاران": "سرمایه‌گذاران",
    "سرمایه گذار": "سرمایه‌گذار",

    "سرمایه گذاری": "سرمایه‌گذاری",
    "سرمایه گذاری‌ها": "سرمایه‌گذاری‌ها",

    "سرمایه‌ گذاری": "سرمایه‌گذاری",

    "می کند": "می‌کند",
    "می شود": "می‌شود",
    "می کنند": "می‌کنند",
    "می کند.": "می‌کند.",
    "می شود.": "می‌شود.",

    "می‌ کند": "می‌کند",
    "می‌ شود": "می‌شود",
    "می‌ کنند": "می‌کنند",

    "هزینه های": "هزینه‌های",
    "داده های": "داده‌های",
    "نرخ های": "نرخ‌های",
    "قیمت های": "قیمت‌های",
    "بازار های": "بازارهای",
    "شرکت های": "شرکت‌های",
    "دارایی های": "دارایی‌های",

    "هزینه‌ های": "هزینه‌های",
    "داده‌ های": "داده‌های",
    "نرخ‌ های": "نرخ‌های",
    "قیمت‌ های": "قیمت‌های",
    "بازار‌ های": "بازارهای",
    "شرکت‌ های": "شرکت‌های",
    "دارایی‌ های": "دارایی‌های",

    "در به عنوان": "در آستانه",

    # ترجمه‌های رایج و اشتباه Google
    "سوار شد": "افزایش یافت",
    "سوار شده": "افزایش یافته",
    "اول است": "در ابتدا است",

    "Edge": "",
    "edge": "",

}


# ============================================================
# English months
# ============================================================

MONTHS = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
}


PERSIAN_MONTHS = [
    "فروردین",
    "اردیبهشت",
    "خرداد",
    "تیر",
    "مرداد",
    "شهریور",
    "مهر",
    "آبان",
    "آذر",
    "دی",
    "بهمن",
    "اسفند",
]


# ============================================================
# Gregorian -> Jalali
# ============================================================

def gregorian_to_jalali(year, month, day):

    gy = year - 1600
    gm = month - 1
    gd = day - 1

    g_days = [
        31, 28, 31, 30, 31, 30,
        31, 31, 30, 31, 30, 31
    ]

    days = (
        365 * gy
        + (gy + 3) // 4
        - (gy + 99) // 100
        + (gy + 399) // 400
    )

    for i in range(gm):
        days += g_days[i]

    if (
        month > 2
        and (
            year % 4 == 0
            and (
                year % 100 != 0
                or year % 400 == 0
            )
        )
    ):
        days += 1

    days += gd

    jy = -1595 + 33 * (days // 12053)

    days %= 12053

    jy += 4 * (days // 1461)

    days %= 1461

    if days > 365:
        jy += (days - 1) // 365
        days = (days - 1) % 365

    if days < 186:
        jm = 1 + days // 31
        jd = 1 + days % 31
    else:
        jm = 7 + (days - 186) // 30
        jd = 1 + (days - 186) % 30

    return jy, jm, jd


def convert_date(year, month, day):

    try:
        datetime(
            year,
            month,
            day
        )

    except ValueError:
        return None

    jy, jm, jd = gregorian_to_jalali(
        year,
        month,
        day
    )

    return (
        f"{jd} {PERSIAN_MONTHS[jm - 1]} {jy}"
    )


# ============================================================
# Date conversion
# ============================================================

def convert_dates_to_jalali(text):

    if not text:
        return ""

    month_pattern = "|".join(
        MONTHS.keys()
    )

    # --------------------------------------------------------
    # August 12, 2026
    # August 12 2026
    # --------------------------------------------------------

    pattern_1 = re.compile(
        r"\b("
        + month_pattern
        + r")\s+"
        r"(\d{1,2})"
        r"(?:,\s*|\s+)"
        r"(\d{4})\b",
        re.IGNORECASE
    )

    def replace_1(match):

        month_name = (
            match.group(1)
            .lower()
        )

        day = int(
            match.group(2)
        )

        year = int(
            match.group(3)
        )

        month = MONTHS.get(
            month_name
        )

        result = convert_date(
            year,
            month,
            day
        )

        return (
            result
            if result
            else match.group(0)
        )

    text = pattern_1.sub(
        replace_1,
        text
    )

    # --------------------------------------------------------
    # 12 August 2026
    # --------------------------------------------------------

    pattern_2 = re.compile(
        r"\b"
        r"(\d{1,2})\s+("
        + month_pattern
        + r")\s+"
        r"(\d{4})\b",
        re.IGNORECASE
    )

    def replace_2(match):

        day = int(
            match.group(1)
        )

        month_name = (
            match.group(2)
            .lower()
        )

        year = int(
            match.group(3)
        )

        month = MONTHS.get(
            month_name
        )

        result = convert_date(
            year,
            month,
            day
        )

        return (
            result
            if result
            else match.group(0)
        )

    text = pattern_2.sub(
        replace_2,
        text
    )

    return text


# ============================================================
# Protect terms
# ============================================================

def protect_terms(text):

    protected = {}

    counter = 0

    terms = sorted(
        PROTECTED_TERMS.items(),
        key=lambda x: len(x[0]),
        reverse=True
    )

    for key, value in terms:

        pattern = re.compile(
            r"(?<![A-Za-z0-9_])"
            + re.escape(key)
            + r"(?![A-Za-z0-9_])",
            re.IGNORECASE
        )

        if not pattern.search(text):
            continue

        # ----------------------------------------------------
        # از placeholder ساده مثل ZZTERM استفاده نمی‌کنیم.
        #
        # Google Translate ممکن است آن را تغییر دهد.
        # ----------------------------------------------------

        marker = (
            f"XQTERM{counter}QX"
        )

        text = pattern.sub(
            marker,
            text
        )

        protected[
            marker
        ] = value

        counter += 1

    return text, protected


# ============================================================
# Restore protected terms
# ============================================================

def restore_terms(
    text,
    protected
):

    if not text:
        return text

    for marker, value in protected.items():

        text = text.replace(
            marker,
            value
        )

    return text


# ============================================================
# Clean text
# ============================================================

def clean_text(text):

    if not text:
        return ""

    text = html.unescape(
        str(text)
    )

    # حذف HTML
    text = re.sub(
        r"<[^>]+>",
        " ",
        text
    )

    # حذف entity
    text = re.sub(
        r"&[a-zA-Z0-9#]+;",
        " ",
        text
    )

    # فاصله‌ها
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

    # اصلاح عبارت‌های شناخته‌شده
    for wrong, correct in REPLACE_WORDS.items():

        text = text.replace(
            wrong,
            correct
        )

    # --------------------------------------------------------
    # حذف تکرار پشت سر هم
    # --------------------------------------------------------

    words = text.split()

    result = []

    for word in words:

        if (
            not result
            or word != result[-1]
        ):
            result.append(word)

    text = " ".join(
        result
    )

    # --------------------------------------------------------
    # علائم نگارشی
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
        r"\s+%",
        "%",
        text
    )

    return text.strip()


# ============================================================
# Detect broken translation
# ============================================================

def good_translation(
    text,
    original=""
):

    if not text:
        return False

    text = text.strip()

    if not text:
        return False

    # --------------------------------------------------------
    # عبارات ممنوع
    # --------------------------------------------------------

    bad_phrases = [

        "XQTERM",
        "ZZTERM",

        "undefined",
        "None",

        "Reg کریپتو",
        "Reg crypto",

        "سوار شد",

        "شما و",

        "اول است",

        "در به عنوان",

        "Click here",
        "Read more",
        "Continue reading",

        "This article",
        "This post",

    ]

    lowered = text.lower()

    for phrase in bad_phrases:

        if phrase.lower() in lowered:
            return False

    # --------------------------------------------------------
    # ترجمه خیلی کوتاه
    # --------------------------------------------------------

    if len(text.split()) < 3:
        return False

    # --------------------------------------------------------
    # اگر متن انگلیسی بوده، ترجمه باید فارسی باشد.
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
            return False

        if (
            english_chars
            > persian_chars * 2
        ):
            return False

    # --------------------------------------------------------
    # اگر خروجی دقیقاً برابر متن انگلیسی باشد
    # --------------------------------------------------------

    if original:

        original_clean = clean_text(
            original
        ).lower()

        translated_clean = clean_text(
            text
        ).lower()

        if (
            original_clean
            and translated_clean == original_clean
        ):
            if english_chars > persian_chars:
                return False

    return True


# ============================================================
# Shorten text
# ============================================================

def shorten(
    text,
    limit=1200
):

    if not text:
        return ""

    text = clean_text(
        text
    )

    if len(text) <= limit:
        return text

    shortened = text[:limit]

    # --------------------------------------------------------
    # اول سعی می‌کنیم در انتهای جمله قطع کنیم.
    # --------------------------------------------------------

    sentence_positions = [

        shortened.rfind("۔"),
        shortened.rfind("."),
        shortened.rfind("؟"),
        shortened.rfind("!"),
    ]

    sentence_end = max(
        sentence_positions
    )

    if sentence_end >= limit * 0.70:

        return shortened[
            :sentence_end + 1
        ].strip()

    # --------------------------------------------------------
    # اگر جمله مناسب نبود، روی فاصله قطع می‌کنیم.
    # --------------------------------------------------------

    last_space = shortened.rfind(
        " "
    )

    if last_space > limit * 0.75:

        shortened = shortened[
            :last_space
        ]

    return shortened.rstrip(
        " .،؛,:-–—"
    ) + "..."


# ============================================================
# Remove duplicated sentences
# ============================================================

def remove_duplicate_sentences(text):

    if not text:
        return ""

    sentences = re.split(
        r"(?<=[.!؟])\s+",
        text
    )

    result = []
    seen = set()

    for sentence in sentences:

        sentence = sentence.strip()

        if not sentence:
            continue

        normalized = re.sub(
            r"\W+",
            "",
            sentence.lower()
        )

        if (
            normalized
            and normalized in seen
        ):
            continue

        seen.add(
            normalized
        )

        result.append(
            sentence
        )

    return " ".join(
        result
    )


# ============================================================
# Main translator
# ============================================================

def translate_text(text):

    if not text:
        return ""

    # --------------------------------------------------------
    # Original text
    # --------------------------------------------------------

    original = clean_text(
        text
    )

    if not original:
        return ""

    # --------------------------------------------------------
    # تاریخ‌ها قبل از ترجمه تبدیل نمی‌شوند.
    #
    # ابتدا تاریخ‌ها را محافظت می‌کنیم تا Google Translate
    # آنها را خراب نکند.
    # --------------------------------------------------------

    date_protected = {}

    date_counter = 0

    month_pattern = "|".join(
        MONTHS.keys()
    )

    date_patterns = [

        re.compile(
            r"\b("
            + month_pattern
            + r")\s+"
            r"(\d{1,2})"
            r"(?:,\s*|\s+)"
            r"(\d{4})\b",
            re.IGNORECASE
        ),

        re.compile(
            r"\b"
            r"(\d{1,2})\s+("
            + month_pattern
            + r")\s+"
            r"(\d{4})\b",
            re.IGNORECASE
        ),
    ]

    working_text = original

    for pattern in date_patterns:

        def protect_date(match):

            nonlocal date_counter

            marker = (
                f"XQDATE{date_counter}QX"
            )

            if match.group(1).lower() in MONTHS:

                month = MONTHS[
                    match.group(1).lower()
                ]

                day = int(
                    match.group(2)
                )

                year = int(
                    match.group(3)
                )

            else:

                day = int(
                    match.group(1)
                )

                month = MONTHS[
                    match.group(2).lower()
                ]

                year = int(
                    match.group(3)
                )

            converted = convert_date(
                year,
                month,
                day
            )

            if converted:

                date_protected[
                    marker
                ] = converted

                date_counter += 1

                return marker

            return match.group(0)

        working_text = pattern.sub(
            protect_date,
            working_text
        )

    try:

        # ----------------------------------------------------
        # Protect technical terms
        # ----------------------------------------------------

        protected_text, protected = protect_terms(
            working_text
        )

        # ----------------------------------------------------
        # Google Translate
        # ----------------------------------------------------

        translator = GoogleTranslator(
            source="en",
            target="fa"
        )

        translated = translator.translate(
            protected_text
        )

        if not translated:
            return ""

        # ----------------------------------------------------
        # Restore technical terms
        # ----------------------------------------------------

        translated = restore_terms(
            translated,
            protected
        )

        # ----------------------------------------------------
        # Restore Jalali dates
        # ----------------------------------------------------

        for marker, date_value in date_protected.items():

            translated = translated.replace(
                marker,
                date_value
            )

        # ----------------------------------------------------
        # Clean
        # ----------------------------------------------------

        translated = clean_text(
            translated
        )

        # ----------------------------------------------------
        # Remove duplicate sentences
        # ----------------------------------------------------

        translated = remove_duplicate_sentences(
            translated
        )

        # ----------------------------------------------------
        # Final date conversion
        #
        # برای تاریخ‌هایی که Google Translate خودش تغییر
        # داده باشد.
        # ----------------------------------------------------

        translated = convert_dates_to_jalali(
            translated
        )

        # ----------------------------------------------------
        # Quality check
        # ----------------------------------------------------

        if not good_translation(
            translated,
            original
        ):

            print(
                "⚠️ ترجمه از نظر کیفیت قابل قبول نبود"
            )

            return ""

        # ----------------------------------------------------
        # Limit length
        # ----------------------------------------------------

        translated = shorten(
            translated,
            1200
        )

        return translated

    except Exception as e:

        print(
            "❌ خطا در ترجمه:",
            e
        )

        return ""


# ============================================================
# Test
# ============================================================

if __name__ == "__main__":

    tests = [

        """
        The Federal Reserve is expected to keep interest rates
        unchanged on August 12, 2026. Investors are watching
        the decision closely.
        """,

        """
        Metaplanet moved more than 5,000 Bitcoin on August 12,
        2026, raising speculation that the company could sell
        part of its holdings.
        """,

        """
        The SEC postponed the long-awaited crypto regulation
        meeting.
        """,

        """
        Bitcoin surged after investors reacted to the latest
        Federal Reserve decision.
        """,

        """
        The company announced a major Bitcoin purchase and said
        it plans to continue expanding its holdings.
        """,
    ]

    for test in tests:

        print(
            "\n"
            + "=" * 60
        )

        print(
            "ORIGINAL:"
        )

        print(
            clean_text(test)
        )

        print(
            "\nTRANSLATED:"
        )

        result = translate_text(
            test
        )

        print(
            result
            if result
            else "❌ ترجمه قابل قبول نبود"
        )
