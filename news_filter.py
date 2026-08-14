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

    "bitcoin etf": 14,
    "ethereum etf": 12,
    "crypto etf": 11,

    "bitcoin": 10,
    "ethereum": 8,

    "cryptocurrency": 5,
    "crypto": 5,
    "blockchain": 4,

    # --------------------------------------------------------
    # Regulation
    # --------------------------------------------------------

    "crypto regulation": 13,
    "regulation": 8,
    "regulatory": 8,

    "sec": 10,
    "cftc": 9,

    # --------------------------------------------------------
    # US government / Trump
    # --------------------------------------------------------

    "donald trump": 13,
    "trump": 10,
    "white house": 9,

    # --------------------------------------------------------
    # Federal Reserve / Economy
    # --------------------------------------------------------

    "federal reserve": 13,

    "interest rates": 10,
    "interest rate": 10,

    "rate cut": 12,
    "rate cuts": 12,

    "rate hike": 11,
    "rate hikes": 11,

    "inflation": 10,
    "recession": 10,

    # --------------------------------------------------------
    # Market events
    # --------------------------------------------------------

    "crash": 12,
    "collapse": 12,

    "plunges": 10,
    "plunge": 10,

    "surge": 8,
    "surges": 8,

    "soars": 8,
    "soar": 8,

    # --------------------------------------------------------
    # Security
    # --------------------------------------------------------

    "security breach": 12,
    "data breach": 12,

    "hacked": 12,
    "hack": 11,

    # --------------------------------------------------------
    # Geopolitics
    # --------------------------------------------------------

    "war": 9,
    "sanctions": 9,

    # --------------------------------------------------------
    # ETF / Institutional
    # --------------------------------------------------------

    "institutional": 6,
    "etf": 3,

    # --------------------------------------------------------
    # Company actions
    # --------------------------------------------------------

    "bankruptcy": 12,
    "liquidation": 11,

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

    text = re.sub(
        r"<[^>]+>",
        " ",
        text
    )

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

    title = re.sub(
        r"[^\w\s]",
        " ",
        title
    )

    title = re.sub(
        r"\s+",
        " ",
        title
    )

    return title.strip()


# ============================================================
# Title similarity
# ============================================================

def title_similarity(
    title1,
    title2
):

    a = set(
        normalize_title(
            title1
        ).split()
    )

    b = set(
        normalize_title(
            title2
        ).split()
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

            # شباهت خیلی بالا
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

def contains_keyword(
    text,
    keyword
):

    if not text or not keyword:
        return False

    text = str(text).lower()
    keyword = str(keyword).lower().strip()

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

    full_text = (
        title
        + " "
        + description
    )

    score = 0

    matched_topics = set()

    # ========================================================
    # Important topics
    # ========================================================

    for keyword, points in IMPORTANT_TOPICS.items():

        if keyword in matched_topics:
            continue

        title_match = contains_keyword(
            title,
            keyword
        )

        full_match = contains_keyword(
            full_text,
            keyword
        )

        if not full_match:
            continue

        if title_match:

            # عنوان وزن کامل می‌گیرد
            score += points

        else:

            # متن وزن کمتر می‌گیرد
            score += points * 0.45

        matched_topics.add(
            keyword
        )

    # ========================================================
    # Urgent
    # ========================================================

    if news.get(
        "urgent",
        False
    ):

        score += 5

    # ========================================================
    # Source
    # ========================================================

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
# Topic focus score
#
# خبر تک‌موضوعی امتیاز بیشتری می‌گیرد.
# ============================================================

def calculate_focus_score(news):

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

    topic_groups = news.get(
        "topic_groups",
        []
    )

    if not isinstance(
        topic_groups,
        list
    ):

        topic_groups = []

    topic_count = len(
        set(topic_groups)
    )

    score = 15

    # --------------------------------------------------------
    # اگر Scraper آن را roundup تشخیص داده
    # --------------------------------------------------------

    if news.get(
        "aggregated",
        False
    ):

        score -= 35

    # --------------------------------------------------------
    # تعداد حوزه‌ها
    # --------------------------------------------------------

    if topic_count <= 1:

        score += 15

    elif topic_count == 2:

        score += 5

    elif topic_count == 3:

        score -= 10

    elif topic_count >= 4:

        score -= 30

    # --------------------------------------------------------
    # عنوان چندموضوعی
    # --------------------------------------------------------

    title_lower = title.lower()

    separators = [
        " and ",
        " as ",
        " while ",
        " amid ",
        " plus ",
        ";",
        ":",
    ]

    separator_count = 0

    for separator in separators:

        separator_count += title_lower.count(
            separator
        )

    if separator_count >= 3:

        score -= 10

    # --------------------------------------------------------
    # متن بسیار طولانی
    # --------------------------------------------------------

    if len(description) > 1000:

        score -= 5

    if len(description) > 1400:

        score -= 10

    return max(
        round(score, 2),
        0
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
    # Description
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
    # Description
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
    # Title repeated in description
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
# News quality score
#
# بررسی می‌کند خبر واقعاً یک خبر مستقل است یا نه.
# ============================================================

def calculate_quality_score(news):

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

    score = 10

    # عنوان خیلی کوتاه
    if len(title) < 25:

        score -= 5

    # description خیلی کوتاه
    if len(description) < 80:

        score -= 5

    # خبرهای خیلی طولانی
    if len(description) > 1500:

        score -= 5

    # تعداد زیاد جمله
    sentence_count = len(
        re.findall(
            r"[.!?]",
            description
        )
    )

    if sentence_count >= 8:

        score -= 5

    if sentence_count >= 12:

        score -= 5

    return max(
        score,
        0
    )


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

    focus = calculate_focus_score(
        news
    )

    quality = calculate_quality_score(
        news
    )

    # ========================================================
    # وزن‌ها
    #
    # اهمیت       35%
    # کامل بودن   20%
    # واضح بودن   15%
    # تمرکز خبر   20%
    # تازگی       10%
    #
    # Quality به صورت bonus/penalty کوچک
    # ========================================================

    final_score = (

        importance * 0.35

        + completeness * 0.20

        + clarity * 0.15

        + focus * 0.20

        + freshness * 0.10

    )

    # Quality adjustment
    final_score += (
        quality - 10
    ) * 0.5

    return round(
        max(final_score, 0),
        2
    )


# ============================================================
# Safe date value
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

        # ----------------------------------------------------
        # امتیازهای جزئی
        # ----------------------------------------------------

        item["importance_score"] = (
            calculate_importance_score(
                item
            )
        )

        item["completeness_score"] = (
            calculate_completeness_score(
                item
            )
        )

        item["clarity_score"] = (
            calculate_clarity_score(
                item
            )
        )

        item["freshness_score"] = (
            calculate_freshness_score(
                item
            )
        )

        item["focus_score"] = (
            calculate_focus_score(
                item
            )
        )

        item["quality_score"] = (
            calculate_quality_score(
                item
            )
        )

        item["score"] = calculate_score(
            item
        )

        ranked.append(
            item
        )

    # --------------------------------------------------------
    # رتبه‌بندی
    # --------------------------------------------------------

    ranked.sort(
        key=lambda x: (
            x.get(
                "score",
                0
            ),
            x.get(
                "focus_score",
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

    # ========================================================
    # ترجیح شدید به خبر مستقل
    #
    # اگر بهترین خبر roundup باشد ولی خبر مستقل مناسبی
    # وجود داشته باشد، خبر مستقل انتخاب می‌شود.
    # ========================================================

    independent_news = [

        item

        for item in ranked

        if not item.get(
            "aggregated",
            False
        )

    ]

    if independent_news:

        # اگر خبر مستقل امتیاز قابل قبول دارد،
        # آن را به roundup ترجیح بده.
        best_independent = independent_news[0]

        best_overall = ranked[0]

        if best_overall.get(
            "aggregated",
            False
        ):

            return best_independent

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

            "aggregated": False,

            "topic_groups": [
                "economy"
            ],

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

            "aggregated": False,

            "topic_groups": [
                "crypto"
            ],

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

            "aggregated": False,

            "topic_groups": [
                "crypto",
                "etf"
            ],

            "date": datetime.now(
                timezone.utc
            ),
        },

        {
            "source": "CNBC",

            "title": (
                "Stocks rise as Trump discusses Iran "
                "while Bitcoin and oil move higher"
            ),

            "description": (
                "US stocks moved higher in morning trading. "
                "President Trump discussed Iran and new "
                "sanctions. Bitcoin also gained while oil "
                "prices rose. OpenAI announced a separate "
                "business update. Investors are watching "
                "the Federal Reserve. "
                "Markets also reacted to new developments "
                "in China and Europe."
            ),

            "urgent": True,

            "aggregated": True,

            "topic_groups": [
                "stocks",
                "geopolitics",
                "crypto",
                "oil",
                "companies",
                "fed"
            ],

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
            "Aggregated:",
            item.get(
                "aggregated",
                False
            )
        )

        print(
            "Topics:",
            item.get(
                "topic_groups",
                []
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
            "Focus:",
            item.get(
                "focus_score",
                0
            )
        )

        print(
            "Quality:",
            item.get(
                "quality_score",
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
            "Aggregated:",
            best.get(
                "aggregated",
                False
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
