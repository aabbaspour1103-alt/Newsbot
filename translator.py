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

    "Bitcoin ETF": "ETF بیت‌کوین",
    "Ethereum ETF": "ETF اتریوم",

    "interest rate": "نرخ بهره",
    "rate hike": "افزایش نرخ بهره",
    "rate cut": "کاهش نرخ بهره",
    "bond traders": "معامله‌گران اوراق قرضه",
    "bond market": "بازار اوراق قرضه",
    "yield": "بازده اوراق قرضه",
    "inflation": "تورم",
    "recession": "رکود اقتصادی"

}



REPLACE_WORDS = {

    "در حاشیه": "در حالت انتظار",
    "افزایش نرخ": "افزایش نرخ بهره",
    "کاهش نرخ": "کاهش نرخ بهره",

    "بازارهای پیش بینی": "بازارهای پیش‌بینی",

    "نهاد تنظیم کننده": "نهاد نظارتی",
    "تنظیم کننده": "نهاد نظارتی",

    "قراردادهای رویداد": "قراردادهای مبتنی بر رویداد",

    "بیسکویت": "",

}



def protect_terms(text):

    protected = {}

    counter = 0


    for key, value in PROTECTED_TERMS.items():

        pattern = re.compile(
            re.escape(key),
            re.IGNORECASE
        )


        if pattern.search(text):

            marker = f"TERM{counter}X"

            text = pattern.sub(
                marker,
                text
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

    text = text.replace(
        " :",
        ":"
    )


    return text.strip()




def shorten(text, limit=500):

    if len(text) <= limit:
        return text


    return text[:limit] + "..."




def translate_text(text):

    if not text:

        return ""


    original = text


    try:

        text, protected = protect_terms(
            text
        )


        translated = GoogleTranslator(
            source="en",
            target="fa"
        ).translate(
            text
        )


        translated = restore_terms(
            translated,
            protected
        )


        translated = clean_text(
            translated
        )


        translated = shorten(
            translated
        )


        return translated



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
