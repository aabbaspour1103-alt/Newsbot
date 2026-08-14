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

    # --------------------------------------------------------
    # Bitcoin / Crypto
    # --------------------------------------------------------

    "bitcoin etf": 12,
    "ethereum etf": 10,

    "bitcoin": 10,
    "ethereum": 8,

    "cryptocurrency": 5,
    "crypto": 5,
    "blockchain": 4,

    # --------------------------------------------------------
    # Regulation
    # --------------------------------------------------------

    "crypto regulation": 12,
    "regulation": 9,
    "regulatory": 9,

    "sec": 10,
    "cftc": 9,

    # --------------------------------------------------------
    # US government / Trump
    # --------------------------------------------------------

    "donald trump": 12,
    "trump": 10,
    "white house": 9,

    # --------------------------------------------------------
    # Federal Reserve / Economy
    # --------------------------------------------------------

    "federal reserve": 12,

    "interest rates": 10,
    "interest rate": 10,

    "rate cut": 11,
    "rate cuts": 11,

    "rate hike": 10,
    "rate hikes": 10,

    "inflation": 9,
    "recession": 9,

    # --------------------------------------------------------
    # Market events
    # --------------------------------------------------------

    "crash": 11,
    "collapse": 11,

    "plunges": 9,
    "plunge": 9,

    "surge": 8,
    "surges": 8,

    "soars": 8,
    "soar": 8,

    # --------------------------------------------------------
    # Security
    # --------------------------------------------------------

    "security breach": 11,
    "data breach": 11,

    "hacked": 11,
    "hack": 10,

    # --------------------------------------------------------
    # Geopolitics
    # --------------------------------------------------------

    "war": 9,
    "sanctions": 8,

    # --------------------------------------------------------
    # ETF / Institutional
    # --------------------------------------------------------

    "institutional": 7,
    "etf": 8,

    # --------------------------------------------------------
    # Company actions
    # --------------------------------------------------------

    "bankruptcy": 11,
    "liquidation": 10,

    "acquisition": 8,
    "merger": 8,
}


# ============================================================
# Weak / garbage phrases
# ============================================================

WEAK_PHRASES = [

    "read more",
    "continue reading",
    "click here",
    "subscribe",
    "advertisement",
    "advertisment",
    "sponsored",
    "sign up",
    "the post",
    "this post",
    "read the full story",
    "read the full article",
]


# ============================================================
# Normalize text
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
# Normalize title
# ============================================================

def normalize_title(title):

    title = normalize_text(
        title
    ).lower()

    # حذف علائم نگارشی
    title = re.sub(
        r"[^\w\s]",
        " ",
        title
    )

    # فاصله‌های اضافی
    title = re.sub(
        r"\s+",
        " ",
        title
    )

    return title.strip()


# ============================================================
# Title similarity
# ============================================================

def title_similarity(title1, title2):

    a = set(
        normalize_title(title1).split()
    )

    b = set(
        normalize_title(title2).split()
    )

    if not a or not b:
        return 0.0

    intersection = len(
        a.intersection(b)
    )

    union = len(
        a.union(b)
    )

    if union == 0:
        return 0.0

    return intersection / union


# ============================================================
# Remove duplicate / almost duplicate news
# ============================================================

def remove_duplicate_news(news):

    if not news:
        return []

    result = []

    for item in news:

        title = item.get(
            "title",
            ""
        )

        if not title:
            continue

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

            # شباهت 75 درصد یا بیشتر
            if similarity >= 0.75:

                duplicate = True
                break

        if not duplicate:

            result.append(
                item
            )

    return result


# ============================================================
# Keyword matching
# ============================================================

def contains_keyword(text, keyword):

    if not text or not keyword:
        return False

    text = text.lower().strip()
    keyword = keyword.lower().strip()

    # --------------------------------------------------------
    # برای عبارت‌های چندکلمه‌ای
    # --------------------------------------------------------

    if " " in keyword:

        pattern = (
            r"(?<![a-z0-9])"
            + re.escape(keyword)
            + r"(?![a-z0-9])"
        )

    else:

        # جلوگیری از خطاهایی مثل:
        #
        # fed -> offered
        # sec -> sector
        # war -> warehouse
        #
        pattern = (
            r"(?<![a-z0-9])"
            + re.escape(keyword)
            + r"(?![a-z0-9])"
        )

    return re.search(
        pattern,
        text,
        flags=re.IGNORECASE
    ) is not None


# ============================================================
# Importance score
# ============================================================

def calculate_importance_score(news):

    title = normalize_text(
        news.get(
            "title",
            ""
        )
    ).lower()

    description = normalize_text(
        news.get(
            "description",
            ""
        )
    ).lower()

    # عنوان اهمیت بیشتری دارد
    title_text = title
    full_text = (
        title
        + " "
        + description
    )

    score = 0

    matched_topics = set()

    # --------------------------------------------------------
    # Topics
    # --------------------------------------------------------

    for keyword, points in IMPORTANT_TOPICS.items():

        if keyword in matched_topics:
            continue

        if contains_keyword(
            full_text,
            keyword
        ):

            # اگر کلمه در عنوان باشد، اهمیت بیشتری دارد
            if contains_keyword(
                title_text,
                keyword
            ):

                score += points

            else:

                score += points * 0.60

            matched_topics.add(
                keyword
            )

    # --------------------------------------------------------
    # Urgent
    # --------------------------------------------------------

    if news.get(
        "urgent",
        False
    ):

        score += 6

    # --------------------------------------------------------
    # Source
    # --------------------------------------------------------

    source = news.get(
        "source",
        ""
    )

    score += SOURCE_SCORES.get(
        source,
        5
    )

    return round(
        score,
        2
    )


# ============================================================
# Completeness score
# ============================================================

def calculate_completeness_score(news):

    title = normalize_text(
        news.get(
            "title",
            ""
        )
    )

    description = normalize_text(
        news.get(
            "description",
            ""
        )
    )

    score = 0

    # --------------------------------------------------------
    # Title
    # --------------------------------------------------------

    if len(title) >= 30:
        score += 5

    if len(title) >= 60:
        score += 3

    # --------------------------------------------------------
    # Description length
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
    # Word count
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
    # Sentence count
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
        news.get(
            "title",
            ""
        )
    )

    description = normalize_text(
        news.get(
            "description",
            ""
        )
    )

    text = (
        title
        + " "
        + description
    ).lower()

    score = 20

    # --------------------------------------------------------
    # Description length
    # --------------------------------------------------------

    if len(description) == 0:

        score -= 10

    elif len(description) < 50:

        score -= 8

    elif len(description) < 100:

        score -= 4

    # --------------------------------------------------------
    # RSS garbage
    # --------------------------------------------------------

    for phrase in WEAK_PHRASES:

        if contains_keyword(
            text,
            phrase
        ):

            score -= 7

    # --------------------------------------------------------
    # Incomplete ending
    # --------------------------------------------------------

    if description.endswith(
        "..."
    ):

        score -= 5

    # --------------------------------------------------------
    # Title repeated inside description
    # --------------------------------------------------------

    normalized_title = normalize_title(
        title
    )

    normalized_description = normalize_title(
        description
    )

    if (
        normalized_title
        and normalized_title in normalized_description
    ):

        score -= 8

    # --------------------------------------------------------
    # Excessive English garbage
    # --------------------------------------------------------

    english_words = len(
        re.findall(
            r"\b[A-Za-z]{2,}\b",
            description
        )
    )

    total_words = len(
        description.split()
    )

    if (
        total_words >= 20
        and english_words > total_words * 0.85
    ):

        score -= 5

    return max(
        round(score, 2),
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

    # --------------------------------------------------------
    # اطمینان از timezone
    # --------------------------------------------------------

    if date.tzinfo is None:

        date = date.replace(
            tzinfo=timezone.utc
        )

    else:

        date = date.astimezone(
            timezone.utc
        )

    now = datetime.now(
        timezone.utc
    )

    hours = (
        now - date
    ).total_seconds() / 3600

    # خبر آینده / تاریخ خراب
    if hours < 0:
        return 0

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
    # وزن‌ها
    #
    # اهمیت        35%
    # کامل بودن    25%
    # واضح بودن    25%
    # تازگی        15%
    #
    # --------------------------------------------------------

    final_score = (

        importance * 0.35

        + completeness * 0.25

        + clarity * 0.25

        + freshness * 0.15

    )

    return round(
        final_score,
        2
    )


# ============================================================
# Safe date value for sorting
# ============================================================

def safe_date_value(news):

    date = news.get(
        "date"
    )

    if not isinstance(
        date,
        datetime
    ):

        return datetime.min.replace(
            tzinfo=timezone.utc
        )

    if date.tzinfo is None:

        return date.replace(
            tzinfo=timezone.utc
        )

    return date.astimezone(
        timezone.utc
    )


# ============================================================
# Rank news
# ============================================================

def rank_news(news_list):

    if not news_list:
        return []

    # --------------------------------------------------------
    # حذف اخبار مشابه
    # --------------------------------------------------------

    news_list = remove_duplicate_news(
        news_list
    )

    ranked = []

    for news in news_list:

        if not news:
            continue

        item = dict(
            news
        )

        item["score"] = calculate_score(
            item
        )

        # امتیازهای جزئی برای Debug
        item["importance_score"] = calculate_importance_score(
            item
        )

        item["completeness_score"] = calculate_completeness_score(
            item
        )

        item["clarity_score"] = calculate_clarity_score(
            item
        )

        item["freshness_score"] = calculate_freshness_score(
            item
        )

        ranked.append(
            item
        )

    # --------------------------------------------------------
    # رتبه‌بندی
    #
    # اول امتیاز
    # سپس تازگی
    # --------------------------------------------------------

    ranked.sort(
        key=lambda x: (
            x.get(
                "score",
                0
            ),
            x.get(
                "freshness_score",
                0
            ),
            safe_date_value(x)
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

    return [
        best
    ]


# ============================================================
# Test
# ============================================================

if __name__ == "__main__":

    test_news = [

        {
            "source": "CNBC",

            "title": (
                "US wholesale prices were unchanged in July"
            ),

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

            "title": (
                "Bitcoin company announces major purchase"
            ),

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

            "title": (
                "SEC delays crypto regulation meeting"
            ),

            "description": (
                "The SEC postponed a long-awaited "
                "meeting about new crypto regulation "
                "in the United States."
            ),

            "urgent": True,

            "date": datetime.now(
                timezone.utc
            ),
        },
    ]

    ranked = rank_news(
        test_news
    )

    print(
        "\n=============================="
    )

    print(
        "RANKED NEWS"
    )

    print(
        "=============================="
    )

    for index, item in enumerate(
        ranked,
        start=1
    ):

        print(
            "\n------------------------------"
        )

        print(
            "Rank:",
            index
        )

        print(
            "Source:",
            item.get(
                "source",
                ""
            )
        )

        print(
            "Title:",
            item.get(
                "title",
                ""
            )
        )

        print(
            "Importance:",
            item.get(
                "importance_score",
                0
            )
        )

        print(
            "Completeness:",
            item.get(
                "completeness_score",
                0
            )
        )

        print(
            "Clarity:",
            item.get(
                "clarity_score",
                0
            )
        )

        print(
            "Freshness:",
            item.get(
                "freshness_score",
                0
            )
        )

        print(
            "Final score:",
            item.get(
                "score",
                0
            )
        )

    best = select_best_news(
        test_news
    )

    print(
        "\n=============================="
    )

    print(
        "BEST NEWS"
    )

    print(
        "=============================="
    )

    if best:

        print(
            "Source:",
            best.get(
                "source",
                ""
            )
        )

        print(
            "Title:",
            best.get(
                "title",
                ""
            )
        )

        print(
            "Score:",
            best.get(
                "score",
                0
            )
        )

    else:

        print(
            "No suitable news found."
        )
