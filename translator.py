from deep_translator import GoogleTranslator


def translate_text(text):

    try:
        translated = GoogleTranslator(
            source="en",
            target="fa"
        ).translate(text)

        return translated

    except Exception:
        return text


if __name__ == "__main__":

    test = "Bitcoin price rises as investors buy more cryptocurrency"

    result = translate_text(test)

    print("English:")
    print(test)

    print("\nPersian:")
    print(result)
