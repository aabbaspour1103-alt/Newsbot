from deep_translator import GoogleTranslator


PROTECTED_TERMS = {

    # Crypto
    "Bitcoin": "بیت‌کوین",
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
    "ETF": "ETF",
    "NFT": "NFT",
    "DeFi": "دیفای",
    "Crypto": "کریپتو",
    "Cryptocurrency": "ارز دیجیتال",
    "Blockchain": "بلاکچین",
    "Exchange": "صرافی",
    "Token": "توکن",

    # Financial
    "Federal Reserve": "فدرال رزرو",
    "Jerome Powell": "جروم پاول",
    "Donald Trump": "دونالد ترامپ",
    "White House": "کاخ سفید",
    "SEC": "SEC",
    "CFTC": "CFTC",
    "Fed": "فدرال رزرو",
    "Bitcoin ETF": "ETF بیت‌کوین",
    "Ethereum ETF": "ETF اتریوم"

}


REPLACE_WORDS = {

    "بیسکویت": "",
    "کاهش گوشه": "دستکاری بازار",
    "گوشه بازار": "دستکاری بازار",
    "بازارهای پیش بینی": "بازارهای پیش‌بینی",
    "بازار پیش بینی": "بازار پیش‌بینی",
    "خود گواهی": "خوداظهاری",
    "خود گواهی‌نامه": "خوداظهاری",
    "قراردادهای رویداد": "قراردادهای مبتنی بر رویداد",
    "قرارداد رویداد": "قرارداد مبتنی بر رویداد",
    "نهاد تنظیم کننده": "نهاد نظارتی",
    "تنظیم کننده": "نهاد نظارتی"

}


def protect_terms(text):

    protected = {}

    for i, (key, value) in enumerate(PROTECTED_TERMS.items()):

        if key.lower() in text.lower():

            marker = f"__TERM{i}__"

            text = text.replace(key, marker)

            protected[marker] = value

    return text, protected


def restore_terms(text, protected):

    for marker, value in protected.items():

        text = text.replace(marker, value)

    return text


def clean_text(text):

    for wrong, correct in REPLACE_WORDS.items():

        text = text.replace(wrong, correct)

    while "  " in text:

        text = text.replace("  ", " ")

    text = text.replace(" ،", "،")
    text = text.replace(" .", ".")
    text = text.replace(" :", ":")

    return text.strip()


def translate_text(text):

    if not text:

        return ""

    original = text

    try:

        text, protected = protect_terms(text)

        translated = GoogleTranslator(
            source="en",
            target="fa"
        ).translate(text)

        translated = restore_terms(
            translated,
            protected
        )

        translated = clean_text(
            translated
        )

        return translated

    except Exception as e:

        print("خطا در ترجمه:", e)

        return original


if __name__ == "__main__":

    test = (
        "The CFTC warned prediction markets about event contracts. "
        "Donald Trump met Federal Reserve officials. "
        "Bitcoin ETF demand increased while Ethereum and Solana prices rose."
    )

    print("English:\n")
    print(test)

    print("\nPersian:\n")
    print(translate_text(test))
