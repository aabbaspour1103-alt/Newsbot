from deep_translator import GoogleTranslator


CRYPTO_TERMS = {

    "Bitcoin": "بیت‌کوین",
    "Ethereum": "اتریوم",
    "Binance": "بایننس",
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
    "Token": "توکن"

}



def protect_terms(text):

    protected = {}

    for i, (key, value) in enumerate(CRYPTO_TERMS.items()):

        if key in text:

            marker = f"TERM{i}"

            text = text.replace(
                key,
                marker
            )

            protected[marker] = value


    return text, protected



def restore_terms(text, protected):

    for key, value in protected.items():

        text = text.replace(
            key,
            value
        )


    return text



def translate_text(text):

    if not text:
        return ""


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


        return translated


    except Exception as e:

        print(
            "خطا در ترجمه:",
            e
        )

        return text



if __name__ == "__main__":

    test = (
        "Bitcoin price rises as investors "
        "buy more cryptocurrency. "
        "Ethereum and Solana market grows."
    )


    print("English:")
    print(test)


    print("\nPersian:")

    print(
        translate_text(test)
    )
