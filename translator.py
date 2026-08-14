from deep_translator import GoogleTranslator
import re
import html
from datetime import datetime


# ============================================================
# Protected terms
# ============================================================

PROTECTED_TERMS = {

    # ---------------- Crypto ----------------

    "Bitcoin": "بیت‌کوین",
    "Bitcoin Core": "Bitcoin Core",
    "Ethereum": "اتریوم",
    "Binance": "بایننس",
    "Binance Coin": "بایننس کوین",
    "BNB": "BNB",
    "Solana": "سولانا",
    "Ripple": "ریپل",
    "XRP": "XRP",
    "Dogecoin": "دوج‌کوین",
    "Shiba Inu": "شیبا اینو",
    "Cardano": "کاردانو",
    "Polygon": "پالیگان",
    "Toncoin": "تون‌کوین",
    "Tether": "تتر",
    "USDT": "USDT",

    # ---------------- Crypto terms ----------------

    "Cryptocurrency": "ارز دیجیتال",
    "Cryptocurrencies": "ارزهای دیجیتال",
    "Crypto": "کریپتو",
    "crypto": "کریپتو",

    "Blockchain": "بلاکچین",
    "blockchain": "بلاکچین",

    "DeFi": "دیفای",
    "NFT": "NFT",
    "DAO": "DAO",
    "Web3": "وب۳",

    "Exchange": "صرافی",
    "Token": "توکن",
    "Tokens": "توکن‌ها",

    "Stablecoin": "استیبل‌کوین",
    "Stablecoins": "استیبل‌کوین‌ها",

    "Bitcoin ETF": "ETF بیت‌کوین",
    "Ethereum ETF": "ETF اتریوم",
    "ETF": "ETF",

    # ---------------- Finance ----------------

    "Federal Reserve": "فدرال رزرو آمریکا",
    "Fed": "فدرال رزرو آمریکا",
    "Jerome Powell": "جروم پاول",

    "SEC": "کمیسیون بورس و اوراق بهادار آمریکا (SEC)",
    "CFTC": "کمیسیون معاملات آتی کالای آمریکا (CFTC)",

    "interest rate": "نرخ بهره",
    "interest rates": "نرخ‌های بهره",

    "rate hike": "افزایش نرخ بهره",
    "rate hikes": "افزایش نرخ بهره",

    "rate cut": "کاهش نرخ بهره",
    "rate cuts": "کاهش نرخ بهره",

    "inflation": "تورم",
    "recession": "رکود اقتصادی",

    "bond market": "بازار اوراق قرضه",
    "bond markets": "بازار اوراق قرضه",

    "bond traders": "معامله‌گران اوراق قرضه",
    "bond yields": "بازده اوراق قرضه",
    "yield": "بازده",

    "stock market": "بازار سهام",
    "stock markets": "بازارهای سهام",

    "shares": "سهام",
    "share": "سهم",

    "investors": "سرمایه‌گذاران",
    "investment": "سرمایه‌گذاری",
    "investments": "سرمایه‌گذاری‌ها",

    "market capitalization": "ارزش بازار",

    "net income": "درآمد خالص",
    "annual threshold": "آستانه سالانه",

    "underlying assets": "دارایی‌های پایه",

    "issuer": "ناشر",
    "provider": "ارائه‌دهنده",

    "Trust": "تراست",

    # ---------------- Companies / Organizations ----------------

    "Hashdex": "Hashdex",
    "Metaplanet": "متاپلنِت",
    "Trezor": "ترزور",

    # ---------------- Important terms ----------------

    "data breach": "نقض داده",
    "data breach": "نقض امنیت داده",

    "hack": "هک",
    "hacked": "هک شد",

    "sanctions": "تحریم‌ها",
    "sanction": "تحریم",

    "breaking news": "خبر فوری",

}


# ============================================================
# Common bad translations / corrections
# ============================================================

REPLACE_WORDS = {

    "Reg کریپتو": "مقررات کریپتو",
    "Reg crypto": "مقررات کریپتو",

    "crypto Reg": "مقررات کریپتو",
    "Crypto Reg": "مقررات کریپتو",

    "ارزهای رمزنگاری شده": "ارزهای دیجیتال",
    "ارز رمزنگاری شده": "ارز دیجیتال",

    "رمزنگاری": "کریپتو",

    "بهره بهره": "بهره",

    "بازده بازده": "بازده",

    "سهام سهام": "سهام",

    "اوراق قرضههای": "اوراق قرضه",
    "اوراق قرضه های": "اوراق قرضه",

    "ارائه دهنده": "ارائه‌دهنده",
    "ارائه‌دهندگان": "ارائه‌دهندگان",

    "سرمایه گذاران": "سرمایه‌گذاران",
    "سرمایه گذاری": "سرمایه‌گذاری",
    "سرمایه گذاری‌ها": "سرمایه‌گذاری‌ها",

    "می کند": "می‌کند",
    "می شود": "می‌شود",
    "می کنند": "می‌کنند",
    "خواهد شد": "خواهد شد",

    "سوار شد": "افزایش یافت",

    "هزینه های": "هزینه‌های",

    "داده های": "داده‌های",

    "نرخ های": "نرخ‌های",

    "قیمت های": "قیمت‌های",

    "بازار های": "بازارهای",

    "شرکت های": "شرکت‌های",

    "دارایی های": "دارایی‌های",

    "در به عنوان": "در آستانه",

    "Edge": "",

}


# ============================================================
# English month names
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

    if month > 2:
        if (
            year % 4 == 0
            and (
                year % 100 != 0
                or year % 400 == 0
            )
        ):
            gy_days = 366
        else:
            gy_days = 365
    else:
        gy_days = 365

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
# Convert English dates inside text
# ============================================================

def convert_dates_to_jalali(text):

    if not text:
        return ""

    # August 12, 2026
    pattern_1 = re.compile(
        r"\b("
        + "|".join(MONTHS.keys())
        + r")\s+"
        r"(\d{1,2}),?\s+"
        r"(\d{4})\b",
        re.IGNORECASE
    )

    def replace_1(match):

        month_name = match.group(1).lower()
        day = int(match.group(2))
        year = int(match.group(3))

        month = MONTHS.get(
            month_name
        )

        result = convert_date(
            year,
            month,
            day
        )

        return result or match.group(0)

    text = pattern_1.sub(
        replace_1,
        text
    )

    # 12 August 2026
    pattern_2 = re.compile(
        r"\b"
        r"(\d{1,2})\s+("
        + "|".join(MONTHS.keys())
        + r")\s+"
        r"(\d{4})\b",
        re.IGNORECASE
    )

    def replace_2(match):

        day = int(match.group(1))
        month_name = match.group(2).lower()
        year = int(match.group(3))

        month = MONTHS.get(
            month_name
        )

        result = convert_date(
            year,
            month,
            day
        )

        return result or match.group(0)

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
            r"(?<!\w)"
            + re.escape(key)
            + r"(?!\w)",
            re.IGNORECASE
        )

        if pattern.search(text):

            marker = f"ZZTERM{counter}ZZ"

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
# Restore terms
# ============================================================

def restore_terms(
    text,
    protected
):

    for marker, value in protected.items():

        text = text.replace(
            marker,
            value
        )

    return text


# ============================================================
# Clean translated text
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

    # حذف entity باقی‌مانده
    text = re.sub(
        r"&[a-zA-Z0-9#]+;",
        " ",
        text
    )

    # فاصله‌ها
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

    # حذف تکرار پشت سر هم کلمات
    words = text.split()

    clean = []

    for word in words:

        if (
            not clean
            or word != clean[-1]
        ):
            clean.append(word)

    text = " ".join(clean)

    # فاصله قبل از علائم
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

    return text.strip()


# ============================================================
# Translation quality check
# ============================================================

def good_translation(text):

    if not text:
        return False

    bad_words = [

        "ZZTERM",
        "undefined",
        "None",

        "سوار شد",

        "شما و",

        "اول است",

        "در به عنوان",

        "Reg کریپتو",

        "Reg crypto",

        "Click here",

        "Read more",

        "Continue reading",

    ]

    lowered = text.lower()

    for bad in bad_words:

        if bad.lower() in lowered:
            return False

    # ترجمه نباید تقریباً کاملاً انگلیسی باقی مانده باشد
    letters = re.findall(
        r"[A-Za-z]",
        text
    )

    persian = re.findall(
        r"[\u0600-\u06FF]",
        text
    )

    if len(text) > 50:

        if (
            len(letters)
            > len(persian) * 2
        ):
            return False

    return len(
        text.split()
    ) >= 4


# ============================================================
# Shorten
# ============================================================

def shorten(
    text,
    limit=1200
):

    if not text:
        return ""

    if len(text) <= limit:
        return text

    shortened = text[:limit]

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
# Main translator
# ============================================================

def translate_text(text):

    if not text:
        return ""

    original = clean_text(
        text
    )

    if not original:
        return ""

    # --------------------------------------------------------
    # تاریخ‌ها را قبل از ترجمه به شمسی تبدیل می‌کنیم
    # --------------------------------------------------------

    original = convert_dates_to_jalali(
        original
    )

    try:

        # ----------------------------------------------------
        # محافظت از اصطلاحات تخصصی
        # ----------------------------------------------------

        protected_text, protected = protect_terms(
            original
        )

        # ----------------------------------------------------
        # Google Translate
        # ----------------------------------------------------

        translated = GoogleTranslator(
            source="en",
            target="fa"
        ).translate(
            protected_text
        )

        if not translated:
            return original

        # ----------------------------------------------------
        # برگرداندن اصطلاحات
        # ----------------------------------------------------

        translated = restore_terms(
            translated,
            protected
        )

        # ----------------------------------------------------
        # پاک‌سازی
        # ----------------------------------------------------

        translated = clean_text(
            translated
        )

        # ----------------------------------------------------
        # اصلاح تاریخ‌ها
        # ----------------------------------------------------

        translated = convert_dates_to_jalali(
            translated
        )

        # ----------------------------------------------------
        # بررسی کیفیت
        # ----------------------------------------------------

        if not good_translation(
            translated
        ):

            return original

        # ----------------------------------------------------
        # محدود کردن طول
        # ----------------------------------------------------

        return shorten(
            translated,
            1200
        )

    except Exception as e:

        print(
            "خطا در ترجمه:",
            e
        )

        return original


# ============================================================
# Test
# ============================================================

if __name__ == "__main__":

    tests = [

        """
        The Federal Reserve is expected to keep interest rates unchanged on August 12, 2026.
        Investors are watching the decision closely.
        """,

        """
        Metaplanet moved more than 5,000 Bitcoin on August 12, 2026,
        raising speculation that the company could sell part of its holdings.
        """,

        """
        The SEC postponed the long-awaited crypto regulation meeting.
        """,

    ]

    for test in tests:

        print(
            "\n--------------------------------"
        )

        print(
            translate_text(test)
        )
