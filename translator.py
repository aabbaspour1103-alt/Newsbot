from deep_translator import GoogleTranslator
import re
import html
from datetime import datetime


# ============================================================
# Protected terms
# ============================================================

PROTECTED_TERMS = {

    # ========================================================
    # Crypto
    # ========================================================

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
    "IBIT": "IBIT",

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

    "Exchanges": "صرافی‌ها",
    "Exchange": "صرافی",

    # ========================================================
    # ETF / Options / Financial instruments
    # ========================================================

    "call options": "اختیارهای خرید",
    "Call options": "اختیارهای خرید",
    "calls": "اختیارهای خرید",
    "Calls": "اختیارهای خرید",

    "put options": "اختیارهای فروش",
    "Put options": "اختیارهای فروش",
    "puts": "اختیارهای فروش",
    "Puts": "اختیارهای فروش",

    "underlying shares": "سهام پایه",
    "Underlying shares": "سهام پایه",

    "underlying assets": "دارایی‌های پایه",
    "Underlying assets": "دارایی‌های پایه",

    "underlying stock": "سهام پایه",
    "underlying securities": "اوراق بهادار پایه",

    "options contracts": "قراردادهای اختیار معامله",
    "option contracts": "قراردادهای اختیار معامله",
    "options contract": "قرارداد اختیار معامله",
    "option contract": "قرارداد اختیار معامله",

    "call contracts": "قراردادهای اختیار خرید",
    "put contracts": "قراردادهای اختیار فروش",

    "filing": "گزارش ثبت‌شده",
    "filings": "گزارش‌های ثبت‌شده",

    "quarterly filing": "گزارش فصلی ثبت‌شده",
    "SEC filing": "گزارش ثبت‌شده نزد SEC",

    "assets under management": "دارایی‌های تحت مدیریت",
    "AUM": "دارایی‌های تحت مدیریت",

    # ========================================================
    # Finance
    # ========================================================

    "Federal Reserve": "فدرال رزرو آمریکا",
    "Fed": "فدرال رزرو آمریکا",

    "Jerome Powell": "جروم پاول",

    "Securities and Exchange Commission":
        "کمیسیون بورس و اوراق بهادار آمریکا (SEC)",

    "SEC":
        "کمیسیون بورس و اوراق بهادار آمریکا (SEC)",

    "CFTC":
        "کمیسیون معاملات آتی کالای آمریکا (CFTC)",

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

    "institutional investors":
        "سرمایه‌گذاران نهادی",

    "investors": "سرمایه‌گذاران",

    "investments": "سرمایه‌گذاری‌ها",
    "investment": "سرمایه‌گذاری",

    "shares": "سهام",
    "share": "سهم",

    "issuers": "ناشران",
    "issuer": "ناشر",

    "providers": "ارائه‌دهندگان",
    "provider": "ارائه‌دهنده",

    "Trust": "تراست",

    "portfolio": "سبد سرمایه‌گذاری",
    "holdings": "دارایی‌ها",
    "holding": "دارایی",

    "trading volume": "حجم معاملات",

    "market maker": "بازارساز",
    "market makers": "بازارسازان",

    "bullish": "صعودی",
    "bearish": "نزولی",

    "outflows": "خروج سرمایه",
    "inflows": "ورود سرمایه",

    "outflow": "خروج سرمایه",
    "inflow": "ورود سرمایه",

    "revenue": "درآمد",
    "profit": "سود",
    "loss": "زیان",

    # ========================================================
    # Companies
    # ========================================================

    "Hashdex": "Hashdex",
    "Metaplanet": "متاپلنِت",
    "Trezor": "ترزور",
    "BlackRock": "بلک‌راک",
    "Coinbase": "کوین‌بیس",

    # ========================================================
    # Security / Regulation
    # ========================================================

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
    "ارزهای رمزنگاری‌شده": "ارزهای دیجیتال",
    "ارز رمزنگاری‌شده": "ارز دیجیتال",

    "رمزنگاری": "کریپتو",

    "بهره بهره": "بهره",
    "بازده بازده": "بازده",
    "سهام سهام": "سهام",

    "اوراق قرضههای": "اوراق قرضه",
    "اوراق قرضه های": "اوراق قرضه",

    # ========================================================
    # Financial corrections
    # ========================================================

    "تماس ها": "اختیارهای خرید",
    "تماس‌ها": "اختیارهای خرید",

    "تماس معادل سهم":
        "سهام معادل قراردادهای اختیار خرید",

    "تماس معادل سهام":
        "سهام معادل قراردادهای اختیار خرید",

    "گزینه های تماس": "اختیارهای خرید",
    "گزینه‌های تماس": "اختیارهای خرید",

    "گزینه های قرار دادن": "اختیارهای فروش",
    "گزینه‌های قرار دادن": "اختیارهای فروش",

    "سهام های پایه": "سهام پایه",
    "سهام پایه ای": "سهام پایه",

    "سهام زیرین": "سهام پایه",
    "سهام زیربنایی": "سهام پایه",

    "بایگانی": "گزارش ثبت‌شده",
    "پرونده": "گزارش ثبت‌شده",

    "دارایی های پایه": "دارایی‌های پایه",

    "قرار می دهد": "می‌رساند",

    "هدف حساب حل نشده باقی ماند":
        "هدف دقیق این معاملات همچنان مشخص نیست",

    "هدف حساب":
        "هدف دقیق معاملات",

    "حل نشده باقی ماند":
        "همچنان مشخص نیست",

    # ========================================================
    # نیم‌فاصله
    # ========================================================

    "ارائه دهنده": "ارائه‌دهنده",
    "ارائه دهندگان": "ارائه‌دهندگان",

    "سرمایه گذار": "سرمایه‌گذار",
    "سرمایه گذاران": "سرمایه‌گذاران",

    "سرمایه گذاری": "سرمایه‌گذاری",
    "سرمایه گذاری‌ها": "سرمایه‌گذاری‌ها",

    "سرمایه‌ گذاری": "سرمایه‌گذاری",

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

    # ========================================================
    # فعل‌ها
    # ========================================================

    "می کند": "می‌کند",
    "می شود": "می‌شود",
    "می کنند": "می‌کنند",

    "می‌ کند": "می‌کند",
    "می‌ شود": "می‌شود",
    "می‌ کنند": "می‌کنند",

    # ========================================================
    # Bad translations
    # ========================================================

    "سوار شد": "افزایش یافت",
    "سوار شده": "افزایش یافته",

    "اول است": "در ابتدا است",

    "در به عنوان": "در آستانه",

    # ========================================================
    # Noise
    # ========================================================

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


# ============================================================
# Convert date
# ============================================================

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
        f"{jd} "
        f"{PERSIAN_MONTHS[jm - 1]} "
        f"{jy}"
    )


# ============================================================
# Convert English dates
# ============================================================

def convert_dates_to_jalali(text):

    if not text:
        return ""

    month_pattern = "|".join(
        MONTHS.keys()
    )

    # ========================================================
    # August 12, 2026
    # ========================================================

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
            match.group(1).lower()
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

    # ========================================================
    # 12 August 2026
    # ========================================================

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
            match.group(2).lower()
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
# Protect technical terms
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

    # خطوط جدید
    text = re.sub(
        r"[\r\n\t]+",
        " ",
        text
    )

    # فاصله اضافی
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    # اصلاح عبارت‌ها
    for wrong, correct in REPLACE_WORDS.items():

        text = text.replace(
            wrong,
            correct
        )

    # حذف تکرار کلمات پشت سر هم
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

    # ========================================================
    # علائم نگارشی
    # ========================================================

    text = re.sub(
        r"\s+،",
        "،",
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
        r"\s+\.",
        ".",
        text
    )

    text = re.sub(
        r"\s+%",
        "%",
        text
    )

    text = re.sub(
        r"\s+,",
        ",",
        text
    )

    return text.strip()


# ============================================================
# Remove duplicate sentences
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

        if normalized:

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
# Financial translation corrections
# ============================================================

def normalize_financial_terms(text):

    if not text:
        return ""

    replacements = {

        # ----------------------------------------------------
        # Options
        # ----------------------------------------------------

        "اختیار خریدها":
            "اختیارهای خرید",

        "اختیار فروشها":
            "اختیارهای فروش",

        "گزینه خرید":
            "اختیار خرید",

        "گزینه فروش":
            "اختیار فروش",

        # ----------------------------------------------------
        # Shares
        # ----------------------------------------------------

        "سهام زیرین":
            "سهام پایه",

        "سهام زیربنایی":
            "سهام پایه",

        "سهم های پایه":
            "سهام پایه",

        "سهام های پایه":
            "سهام پایه",

        # ----------------------------------------------------
        # Filing
        # ----------------------------------------------------

        "بایگانی":
            "گزارش ثبت‌شده",

        "پرونده":
            "گزارش ثبت‌شده",

        # ----------------------------------------------------
        # ETF
        # ----------------------------------------------------

        "ETF بیت کوین":
            "ETF بیت‌کوین",

        "ETF اتریوم":
            "ETF اتریوم",

        # ----------------------------------------------------
        # Known bad machine translations
        # ----------------------------------------------------

        "تماس معادل سهم":
            "سهام معادل قراردادهای اختیار خرید",

        "تماس معادل سهام":
            "سهام معادل قراردادهای اختیار خرید",

        "هدف حساب حل نشده باقی ماند":
            "هدف دقیق این معاملات همچنان مشخص نیست",

        "هدف حساب":
            "هدف دقیق معاملات",

        "حل نشده باقی ماند":
            "همچنان مشخص نیست",

        "افزایش 24 برابری":
            "افزایش ۲۴ برابری",

        "کاهش 52.75 درصدی":
            "کاهش ۵۲٫۷۵ درصدی",

        "به 1.95 میلیون":
            "به ۱٫۹۵ میلیون",
    }

    for wrong, correct in replacements.items():

        text = text.replace(
            wrong,
            correct
        )

    return text


# ============================================================
# Convert Western digits to Persian digits
# ============================================================

def persian_digits(text):

    if not text:
        return ""

    table = str.maketrans(
        "0123456789",
        "۰۱۲۳۴۵۶۷۸۹"
    )

    return text.translate(
        table
    )


# ============================================================
# RTL / LTR formatting
# ============================================================

def apply_rtl(text):

    if not text:
        return ""

    RLM = "\u200F"
    LRM = "\u200E"

    text = text.strip()

    # ========================================================
    # Protect English technical terms
    # ========================================================

    def protect_ltr(match):

        value = match.group(0)

        return (
            LRM
            + value
            + LRM
        )

    text = re.sub(
        r"[A-Za-z][A-Za-z0-9._/-]*",
        protect_ltr,
        text
    )

    # ========================================================
    # Protect numbers and percentages
    # ========================================================

    def protect_numbers(match):

        value = match.group(0)

        return (
            LRM
            + value
            + LRM
        )

    text = re.sub(
        r"\d+(?:[.,٫]\d+)?%?",
        protect_numbers,
        text
    )

    # ========================================================
    # Split sentences
    # ========================================================

    parts = re.split(
        r"(?<=[.!؟])\s+",
        text
    )

    rtl_parts = []

    for part in parts:

        part = part.strip()

        if not part:
            continue

        # جهت RTL برای هر جمله
        part = (
            RLM
            + part
            + RLM
        )

        rtl_parts.append(
            part
        )

    return "\n".join(
        rtl_parts
    ).strip()


# ============================================================
# Translation quality
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

    bad_phrases = [

        "XQTERM",
        "XQDATE",
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

    # ========================================================
    # Too short
    # ========================================================

    if len(text.split()) < 3:

        return False

    # ========================================================
    # Persian detection
    # ========================================================

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

    # ========================================================
    # Same as original
    # ========================================================

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
            and english_chars > persian_chars
        ):

            return False

    return True


# ============================================================
# Shorten
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

    last_space = shortened.rfind(
        " "
    )

    if last_space > limit * 0.75:

        shortened = shortened[
            :last_space
        ]

    return (
        shortened.rstrip(
            " .،؛,:-–—"
        )
        + "..."
    )


# ============================================================
# Protect dates
# ============================================================

def protect_dates(text):

    protected = {}

    counter = 0

    month_pattern = "|".join(
        MONTHS.keys()
    )

    patterns = [

        # August 12, 2026
        re.compile(
            r"\b("
            + month_pattern
            + r")\s+"
            r"(\d{1,2})"
            r"(?:,\s*|\s+)"
            r"(\d{4})\b",
            re.IGNORECASE
        ),

        # 12 August 2026
        re.compile(
            r"\b"
            r"(\d{1,2})\s+("
            + month_pattern
            + r")\s+"
            r"(\d{4})\b",
            re.IGNORECASE
        ),
    ]

    working_text = text

    for pattern in patterns:

        def replace_date(match):

            nonlocal counter

            marker = (
                f"XQDATE{counter}QX"
            )

            # August 12 2026
            if (
                match.group(1).lower()
                in MONTHS
            ):

                month = MONTHS[
                    match.group(1).lower()
                ]

                day = int(
                    match.group(2)
                )

                year = int(
                    match.group(3)
                )

            # 12 August 2026
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

            if not converted:

                return match.group(0)

            protected[
                marker
            ] = converted

            counter += 1

            return marker

        working_text = pattern.sub(
            replace_date,
            working_text
        )

    return (
        working_text,
        protected
    )


# ============================================================
# Restore dates
# ============================================================

def restore_dates(
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
# Main translator
# ============================================================

def translate_text(text):

    if not text:

        return ""

    # ========================================================
    # Original
    # ========================================================

    original = clean_text(
        text
    )

    if not original:

        return ""

    try:

        # ====================================================
        # Protect dates
        # ====================================================

        working_text, date_protected = protect_dates(
            original
        )

        # ====================================================
        # Protect technical terms
        # ====================================================

        protected_text, protected_terms = protect_terms(
            working_text
        )

        # ====================================================
        # Google Translate
        # ====================================================

        translator = GoogleTranslator(
            source="en",
            target="fa"
        )

        translated = translator.translate(
            protected_text
        )

        if not translated:

            return ""

        # ====================================================
        # Restore technical terms
        # ====================================================

        translated = restore_terms(
            translated,
            protected_terms
        )

        # ====================================================
        # Restore Jalali dates
        # ====================================================

        translated = restore_dates(
            translated,
            date_protected
        )

        # ====================================================
        # Clean
        # ====================================================

        translated = clean_text(
            translated
        )

        # ====================================================
        # Financial corrections
        # ====================================================

        translated = normalize_financial_terms(
            translated
        )

        # ====================================================
        # Remove duplicate sentences
        # ====================================================

        translated = remove_duplicate_sentences(
            translated
        )

        # ====================================================
        # Convert dates Google may have changed
        # ====================================================

        translated = convert_dates_to_jalali(
            translated
        )

        # ====================================================
        # Final cleanup
        # ====================================================

        translated = clean_text(
            translated
        )

        translated = normalize_financial_terms(
            translated
        )

        # ====================================================
        # Quality check
        # ====================================================

        if not good_translation(
            translated,
            original
        ):

            print(
                "⚠️ ترجمه از نظر کیفیت قابل قبول نبود"
            )

            return ""

        # ====================================================
        # Persian digits
        # ====================================================

        translated = persian_digits(
            translated
        )

        # ====================================================
        # Limit length
        # ====================================================

        translated = shorten(
            translated,
            1200
        )

        # ====================================================
        # RTL formatting
        # ====================================================

        translated = apply_rtl(
            translated
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
        Bitcoin ETF calls surge 24-fold as puts fall 52.75%,
        reaching 1.95 million IBIT underlying shares.
        """,

        """
        UBS reported 1.95 million IBIT underlying shares
        tied to call options in its August 13 filing.
        """,

        """
        The Federal Reserve is expected to keep
        interest rates unchanged on August 12, 2026.
        Investors are watching the decision closely.
        """,

        """
        Metaplanet moved more than 5,000 Bitcoin
        on August 12, 2026, raising speculation
        that the company could sell part of its holdings.
        """,

        """
        The SEC postponed the long-awaited
        crypto regulation meeting.
        """,

        """
        Bitcoin surged after investors reacted
        to the latest Federal Reserve decision.
        """,
    ]

    for test in tests:

        print(
            "\n"
            + "=" * 70
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
