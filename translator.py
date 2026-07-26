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

    # Crypto terms
    "ETF": "ETF",
    "NFT": "NFT",
    "DeFi": "دیفای",
    "Crypto": "کریپتو",
    "Cryptocurrency": "ارز دیجیتال",
    "Blockchain": "بلاکچین",
    "Exchange": "صرافی",
    "Token": "توکن",

    # ETF / Finance
    "Hashdex": "Hashdex",
    "Trust": "تراست",
    "Shares": "سهام",
    "share": "سهم",
    "provider": "ارائه‌دهنده",
    "issuer": "ناشر",
    "underlying assets": "دارایی‌های پایه",
    "net income": "درآمد خالص",
    "annual threshold": "آستانه سالانه",

    "Federal Reserve": "فدرال رزرو آمریکا",
    "Fed": "فدرال رزرو آمریکا",
    "Jerome Powell": "جروم پاول",

    "SEC": "کمیسیون بورس آمریکا (SEC)",
    "CFTC": "کمیسیون معاملات آتی کالا آمریکا (CFTC)",

    "interest rate": "نرخ بهره",
    "rate hike": "افزایش نرخ بهره",
    "rate cut": "کاهش نرخ بهره",

    "bond traders": "معامله‌گران اوراق قرضه",
    "bond market": "بازار اوراق قرضه",
    "bond yields": "بازده اوراق قرضه",
    "yield": "بازده",

    "inflation": "تورم",
    "recession": "رکود اقتصادی"
}



REPLACE_WORDS = {

    "بهره بهره": "بهره",
    "اوراق قرضههای": "اوراق قرضه",
    "اوراق قرضه های": "اوراق قرضه",
    "در به عنوان": "در آستانه",
    "سوار شد": "افزایش یافت",
    "هزینه های ارائه دهنده اول": "هزینه‌های ارائه‌دهنده",
    "ارائه دهنده اول": "ارائه‌دهنده",
    "سهام اولیه شما": "سهام پایه",
    "می کندهزینه": "می‌کند. هزینه",
    "های سهام": "سهام",
    "بازده بازده": "بازده",
    "Edge": "",

}



def protect_terms(text):

    protected = {}

    counter = 0

    # طولانی‌ترها اول
    terms = sorted(
        PROTECTED_TERMS.items(),
        key=lambda x: len(x[0]),
        reverse=True
    )


    for key, value in terms:

        pattern = re.compile(
            re.escape(key),
            re.IGNORECASE
        )

        if pattern.search(text):

            marker = f"ZZTERM{counter}ZZ"

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


    # حذف تکرار کلمات
    words = text.split()

    clean = []

    for w in words:

        if not clean or w != clean[-1]:
            clean.append(w)


    text = " ".join(clean)


    # فاصله‌ها
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


    bad_words = [

        "ZZTERM",
        "undefined",
        "None",
        "سوار شد",
        "شما و",
        "اول است"

    ]


    for bad in bad_words:

        if bad in text:
            return False


    return len(text.split()) >= 4



def shorten(text, limit=700):

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
    Hashdex crypto ETF keeps 100% of bond yield returns.
    Above the annual threshold, 40% goes to Hashdex and 60% goes to the Trust.
    """

    print(
        translate_text(test)
    )
