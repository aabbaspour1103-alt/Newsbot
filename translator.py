from deep_translator import GoogleTranslator
import re


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

    # Finance
    "Federal Reserve": "فدرال رزرو آمریکا",
    "Fed": "فدرال رزرو آمریکا",
    "Jerome Powell": "جروم پاول",
    "Donald Trump": "دونالد ترامپ",
    "White House": "کاخ سفید",

    "SEC": "کمیسیون بورس آمریکا (SEC)",
    "CFTC": "کمیسیون معاملات آتی کالا آمریکا (CFTC)",

    "interest rate": "نرخ بهره",
    "rate hike": "افزایش نرخ بهره",
    "rate cut": "کاهش نرخ بهره",

    "bond traders": "معامله‌گران اوراق قرضه",
    "bond market": "بازار اوراق قرضه",
    "bond yields": "بازده اوراق قرضه",
    "yield": "بازده اوراق قرضه",

    "inflation": "تورم",
    "recession": "رکود اقتصادی"

}



REPLACE_WORDS = {

    "بهره بهره": "بهره",
    "اوراق قرضهs": "اوراق قرضه",
    "در به عنوان": "در آستانه",
    "به عنوان خطرات": "با افزایش نگرانی‌ها درباره",
    "سوار شد": "آماده شد",
    "Edge": "",

    "بازارهای پیش بینی": "بازارهای پیش‌بینی",
    "نهاد تنظیم کننده": "نهاد نظارتی",
    "تنظیم کننده": "نهاد نظارتی",

}



def protect_terms(text):

    protected = {}

    counter = 0


    for key, value in PROTECTED_TERMS.items():

        if key.lower() in text.lower():

            marker = f"ZZTERM{counter}ZZ"

            text = re.sub(
                key,
                marker,
                text,
                flags=re.IGNORECASE
            )

            protected[marker] = value

            counter += 1


    return text, protected



def restore_terms(text, protected):

    for marker, value in protected.items():

        text = text.replace(
            marker,
            value
        )

    return text



def clean_text(text):

    if not text:
        return ""


    for wrong, correct in REPLACE_WORDS.items():

        text = text.replace(
            wrong,
            correct
        )


    # حذف کلمات تکراری پشت سر هم
    words = text.split()

    result = []

    for word in words:

        if not result or word != result[-1]:
            result.append(word)


    text = " ".join(result)


    # حذف حروف انگلیسی چسبیده به فارسی
    text = re.sub(
        r"([آ-ی])([a-zA-Z]+)",
        r"\1",
        text
    )


    text = re.sub(
        r"\s+",
        " ",
        text
    )


    text = text.replace(
        " ،",
        "،"
    )


    text = text.replace(
        " .",
        "."
    )


    return text.strip()



def good_translation(text):

    if not text:
        return False


    bad = [

        "ZZTERM",
        "undefined",
        "None",
        "در به عنوان",
        "سوار شد"

    ]


    for item in bad:

        if item in text:
            return False


    return len(text.split()) >= 3



def shorten(text, limit=600):

    if len(text) <= limit:

        return text


    return text[:limit] + "..."



def translate_text(text):

    if not text:

        return ""


    original = clean_text(text)


    try:

        protected_text, protected = protect_terms(
            original
        )


        translated = GoogleTranslator(
            source="en",
            target="fa"
        ).translate(
            protected_text
        )


        translated = restore_terms(
            translated,
            protected
        )


        translated = clean_text(
            translated
        )


        if not good_translation(translated):

            return original


        return shorten(
            translated
        )


    except Exception as e:

        print(
            "خطا در ترجمه:",
            e
        )

        return original



if __name__ == "__main__":

    test = """
    Bond traders are watching the Federal Reserve decision.
    Bitcoin ETF demand increased while Ethereum prices rose.
    """

    print(
        translate_text(test)
    )
