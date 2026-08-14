import re
from datetime import datetime, timezone


# ============================================================
# Source importance
# ============================================================

SOURCE_SCORES = {

    # Crypto
    "CoinDesk": 10,
    "Cointelegraph": 8,
    "Decrypt": 8,
    "The Block": 10,
    "CryptoSlate": 8,
    "Bitcoin Magazine": 8,

    # Markets
    "Bloomberg": 10,
    "CNBC": 9,
    "Reuters": 10,
}


# ============================================================
# Important topics
# ============================================================

IMPORTANT_TOPICS = {

    # Bitcoin / Crypto
    "bitcoin": 10,
    "ethereum": 8,
    "bitcoin etf": 10,
    "ethereum etf": 8,
    "crypto": 5,
    "cryptocurrency": 5,
    "blockchain": 4,

    # Regulation
    "sec": 10,
    "cftc": 9,
    "regulation": 9,
    "regulatory": 9,
    "crypto regulation": 10,

    # US government / Trump
    "trump": 10,
    "donald trump": 10,
    "white house": 9,

    # Federal Reserve / economy
    "federal reserve": 10,
    "fed": 9,
    "interest rate": 10,
    "rate cut": 10,
    "rate hike": 9,
    "inflation": 9,
    "recession": 9,

    # Market events
    "crash": 10,
    "collapse": 10,
    "surge": 7,
    "soars": 7,
    "plunges": 8,

    # Security
    "hack": 10,
    "hacked": 10,
    "data breach": 10,
    "security breach": 10,

    # Geopolitics
    "war": 9,
    "sanctions": 8,

    # ETF / institutional
    "etf": 8,
    "institutional": 7,

    # Company actions
    "acquisition": 7,
    "merger": 7,
    "bankruptcy": 10,
    "liquidation": 9,
}


# ============================================================
# Words that usually indicate incomplete / weak content
# ============================================================

WEAK_PHRASES = [

    "read more",
    "continue reading",
    "click here",
    "subscribe",
    "advertisement",
    "the post",
    "this post",
]


# ============================================================
# Clean text
# ============================================================

def normalize_text(text):

    if not text:
        return ""

    text = str(text)

    # حذف HTML
    text = re.sub(
        r"<[^>]+>",
        " ",
        text
    )

    # فاصله‌های اضافی
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# Detect duplicate / almost duplicate titles
# ============================================================

def normalize_title(title):

    title = normalize_text(
        title
    ).lower()

    # حذف علائم نگارشی
    title = re.sub(
        r"[^\w\s]",
        "",
        title
    )

    # حذف فاصله‌های اضافه
    title = re.sub(
        r"\s+",
        " ",
        title
    )

    return title.strip()


def title_similarity(title1, title2):

    a = set(
        normalize_title(title1).split()
    )

    b = set(
        normalize_title(title2).split()
    )

    if not a or not b:
        return 0

    intersection = len(
        a.intersection(b)
    )

    union = len(
        a.union(b)
    )

    return intersection / union


def remove_duplicate_news(news):

    result = []

    for item in news:

        title = item.get(
            "title",
            ""
        )

        duplicate = False

        for existing in result:

            existing_title = existing.get(
                "title",
                ""
            )

            similarity = title_similarity(
                title,
                existing_title
            )

            # بیش از 75٪ شباهت
            if similarity >= 0.75:

                duplicate = True
                break

        if not duplicate:
            result.append(item)

    return result


# ============================================================
# Importance score
# ============================================================

def calculate_importance_score(news):

    title = normalize_text(
        news.get("title", "")
    ).lower()

    description = normalize_text(
        news.get("description", "")
    ).lower()

    full_text = (
        title
        + " "
        + description
    )

    score = 0

    # --------------------------------------------------------
    # موضوع
    # --------------------------------------------------------

    matched_topics = set()

    for keyword, points in IMPORTANT_TOPICS.items():

        if keyword in full_text:

            if keyword not in matched_topics:

                score += points
                matched_topics.add(
                    keyword
                )

    # --------------------------------------------------------
    # خبر فوری
    # --------------------------------------------------------

    if news.get("urgent"):

        score += 8

    # --------------------------------------------------------
    # منبع معتبر
    # --------------------------------------------------------

    source = news.get(
        "source",
        ""
    )

    score += SOURCE_SCORES.get(
        source,
        5
    )

    return score


# ============================================================
# Completeness score
# ============================================================

def calculate_completeness_score(news):

    title = normalize_text(
        news.get("title", "")
    )

    description = normalize_text(
        news.get("description", "")
    )

    score = 0

    # --------------------------------------------------------
    # عنوان مناسب
    # --------------------------------------------------------

    if len(title) >= 30:
        score += 5

    if len(title) >= 60:
        score += 3

    # --------------------------------------------------------
    # توضیحات
    # --------------------------------------------------------

    description_length = len(
        description
    )

    if description_length >= 100:
        score += 10

    if description_length >= 200:
        score += 10

    if description_length >= 350:
        score += 10

    if description_length >= 500:
        score += 5

    # --------------------------------------------------------
    # تعداد کلمات
    # --------------------------------------------------------

    word_count = len(
        description.split()
    )

    if word_count >= 30:
        score += 5

    if word_count >= 60:
        score += 5

    if word_count >= 100:
        score += 5

    # --------------------------------------------------------
    # جملات
    # --------------------------------------------------------

    sentence_count = len(
        re.findall(
            r"[.!?]",
            description
        )
    )

    if sentence_count >= 2:
        score += 5

    if sentence_count >= 3:
        score += 5

    return score


# ============================================================
# Clarity score
# ============================================================

def calculate_clarity_score(news):

    title = normalize_text(
        news.get("title", "")
    )

    description = normalize_text(
        news.get("description", "")
    )

    text = (
        title
        + " "
        + description
    ).lower()

    score = 20

    # --------------------------------------------------------
    # متن‌های خیلی کوتاه
    # --------------------------------------------------------

    if len(description) < 50:
        score -= 12

    elif len(description) < 100:
        score -= 6

    # --------------------------------------------------------
    # RSS garbage
    # --------------------------------------------------------

    for phrase in WEAK_PHRASES:

        if phrase in text:
            score -= 8

    # --------------------------------------------------------
    # متن ناقص
    # --------------------------------------------------------

    if description.endswith(
        "..."
    ):
        score -= 5

    # --------------------------------------------------------
    # تکرار عنوان در توضیحات
    # --------------------------------------------------------

    normalized_title = normalize_title(
        title
    )

    normalized_description = normalize_title(
        description
    )

    if (
        normalized_title
        and normalized_title
        in normalized_description
    ):
        score -= 8

    return max(
        score,
        0
    )


# ============================================================
# Freshness score
# ============================================================

def calculate_freshness_score(news):

    date = news.get(
        "date"
    )

    if not isinstance(
        date,
        datetime
    ):
        return 0

    if date.year == 1:
        return 0

    now = datetime.now(
        timezone.utc
    )

    hours = (
        now - date
    ).total_seconds() / 3600

    if hours <= 2:
        return 10

    if hours <= 6:
        return 8

    if hours <= 12:
        return 6

    if hours <= 24:
        return 4

    if hours <= 48:
        return 2

    return 0


# ============================================================
# Final score
# ============================================================

def calculate_score(news):

    importance = calculate_importance_score(
        news
    )

    completeness = calculate_completeness_score(
        news
    )

    clarity = calculate_clarity_score(
        news
    )

    freshness = calculate_freshness_score(
        news
    )

    # --------------------------------------------------------
    # وزن نهایی
    # --------------------------------------------------------
    #
    # اهمیت       : 30%
    # کامل بودن   : 30%
    # واضح بودن   : 25%
    # تازگی       : 15%
    #
    # اعتبار منبع داخل importance لحاظ شده است.
    # --------------------------------------------------------

    final_score = (
        importance * 0.30
        + completeness * 0.30
        + clarity * 0.25
        + freshness * 0.15
    )

    return round(
        final_score,
        2
    )


# ============================================================
# Rank news
# ============================================================

def rank_news(news_list):

    if not news_list:
        return []

    # حذف اخبار مشابه
    news_list = remove_duplicate_news(
        news_list
    )

    ranked = []

    for news in news_list:

        item = dict(
            news
        )

        item["score"] = calculate_score(
            item
        )

        ranked.append(
            item
        )

    ranked.sort(
        key=lambda x: (
            x.get("score", 0),
            x.get("date", datetime.min)
        ),
        reverse=True
    )

    return ranked


# ============================================================
# Select ONE best news
# ============================================================

def select_best_news(news_list):

    ranked = rank_news(
        news_list
    )

    if not ranked:
        return None

    return ranked[0]


# ============================================================
# Backward-compatible helper
# ============================================================

def filter_news(news_list):

    """
    خروجی فقط یک خبر است.
    """

    best = select_best_news(
        news_list
    )

    if best is None:
        return []

    return [best]


# ============================================================
# Test
# ============================================================

if __name__ == "__main__":

    test_news = [

        {
            "source": "CNBC",
            "title": "US wholesale prices were unchanged in July",
            "description": (
                "Wholesale prices in the United States "
                "were unchanged in July, according to new "
                "government data released Friday. "
                "Economists had expected the producer price "
                "index to increase by 0.2 percent."
            ),
            "urgent": False,
            "date": datetime.now(
                timezone.utc
            ),
        },

        {
            "source": "Bitcoin Magazine",
            "title": "Bitcoin company announces major purchase",
            "description": (
                "The company announced a major new "
                "Bitcoin purchase and said it plans "
                "to continue expanding its holdings."
            ),
            "urgent": False,
            "date": datetime.now(
                timezone.utc
            ),
        },

        {
            "source": "CoinDesk",
            "title": "SEC delays crypto regulation meeting",
            "description": "",
            "urgent": True,
            "date": datetime.now(
                timezone.utc
            ),
        },
    ]

    ranked = rank_news(
        test_news
    )

    for item in ranked:

        print(
            "\n--------------------------"
        )

        print(
            "Source:",
            item["source"]
        )

        print(
            "Title:",
            item["title"]
        )

        print(
            "Score:",
            item["score"]
        )

    best = select_best_news(
        test_news
    )

    print(
        "\n=========================="
    )

    if best:

        print(
            "BEST NEWS:"
        )

        print(
            best["title"]
        )

        print(
            "Score:",
            best["score"]
        )
