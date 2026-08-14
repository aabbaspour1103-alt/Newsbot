import feedparser
import hashlib
import html
import json
import os
import re
from datetime import datetime, timezone


# ============================================================
# News sources
# ============================================================

NEWS_SOURCES = {

    # Crypto
    "CoinDesk": "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "Cointelegraph": "https://cointelegraph.com/rss",
    "Decrypt": "https://decrypt.co/feed",
    "The Block": "https://www.theblock.co/rss.xml",
    "CryptoSlate": "https://cryptoslate.com/feed/",
    "Bitcoin Magazine": "https://bitcoinmagazine.com/.rss/full/",

    # Markets
    "Bloomberg": "https://feeds.bloomberg.com/markets/news.rss",
    "CNBC": "https://www.cnbc.com/id/100003114/device/rss/rss.html",
    "Reuters": "https://feeds.reuters.com/reuters/businessNews",
}


SAVE_FILE = "sent_news.json"


# ============================================================
# Urgent words
# ============================================================

URGENT_WORDS = [

    "Trump",
    "Donald Trump",

    "Federal Reserve",
    "Fed",

    "interest rate",
    "interest rates",
    "rate cut",
    "rate cuts",
    "rate hike",
    "rate hikes",

    "Bitcoin ETF",
    "Ethereum ETF",
    "ETF",

    "SEC",
    "CFTC",

    "hack",
    "hacked",
    "data breach",
    "security breach",

    "crash",
    "collapse",

    "war",
    "sanctions",

    "breaking",
    "breaking news",
    "emergency",

    "approval",
    "approved",

    "ban",
    "banned",

    "regulation",
    "regulatory",
    "crypto regulation",
]


CRYPTO_SOURCES = {
    "CoinDesk",
    "Cointelegraph",
    "Decrypt",
    "The Block",
    "CryptoSlate",
    "Bitcoin Magazine",
}


# ============================================================
# Possible RSS roundup / multi-news indicators
# ============================================================

ROUNDUP_PHRASES = [

    "top stories",
    "top news",
    "morning briefing",
    "daily briefing",
    "news roundup",
    "market roundup",
    "weekly roundup",
    "daily roundup",
    "here are the latest",
    "here's what you need to know",
    "what you need to know",
    "in other news",
    "other news",
    "meanwhile",
    "separately",
    "also in the news",
    "more news",
    "other headlines",
]


# عباراتی که معمولاً شروع خبر جدید یا موضوع جدید را نشان می‌دهند.
STORY_SHIFT_PHRASES = [

    "meanwhile",
    "separately",
    "in other news",
    "another development",
    "elsewhere",
    "also",
    "in a separate move",
    "in a separate development",
    "on another front",
]


# ============================================================
# Sent news
# ============================================================

def load_sent():

    if not os.path.exists(SAVE_FILE):
        return []

    try:

        with open(
            SAVE_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            data = json.load(f)

            if isinstance(data, list):
                return data

    except Exception:
        pass

    return []


def save_sent(data):

    try:

        # فقط 1000 خبر آخر نگهداری شود.
        data = list(
            dict.fromkeys(data)
        )

        with open(
            SAVE_FILE,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                data[-1000:],
                f,
                ensure_ascii=False,
                indent=2
            )

    except Exception:
        pass


def mark_as_sent(news_item):

    if not news_item:
        return

    sent = load_sent()

    news_id_value = news_item.get(
        "id"
    )

    if not news_id_value:
        return

    if news_id_value not in sent:
        sent.append(
            news_id_value
        )

    save_sent(sent)


# ============================================================
# Text cleaning
# ============================================================

def clean_text(text):

    if not text:
        return ""

    # تبدیل HTML entity ها
    text = html.unescape(
        str(text)
    )

    # حذف HTML
    text = re.sub(
        r"<[^>]+>",
        " ",
        text
    )

    # حذف URL
    text = re.sub(
        r"https?://\S+",
        " ",
        text
    )

    # حذف entityهای باقی‌مانده
    text = re.sub(
        r"&[a-zA-Z0-9#]+;",
        " ",
        text
    )

    # تبدیل خط جدید و tab به فاصله
    text = re.sub(
        r"[\r\n\t]+",
        " ",
        text
    )

    # فاصله‌های چندتایی
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# Remove RSS / website rubbish
# ============================================================

def remove_rubbish(text):

    if not text:
        return ""

    patterns = [

        # Website leftovers
        r"The post .*? first appeared on .*",
        r"The post .*? appeared first on .*",
        r"Read more.*",
        r"Continue reading.*",
        r"Continue Reading.*",
        r"Read the full story.*",
        r"Read the full article.*",

        # Subscription / advertising
        r"Subscribe.*",
        r"Advertisement.*",
        r"Advertisment.*",
        r"Sponsored.*",
        r"Sign up.*",
        r"Click here.*",

        # Copyright
        r"©.*",

        # Common RSS leftovers
        r"This article originally appeared.*",
        r"This story originally appeared.*",
        r"Originally published.*",
    ]

    for pattern in patterns:

        text = re.sub(
            pattern,
            "",
            text,
            flags=re.IGNORECASE
        )

    return clean_text(text)


# ============================================================
# Remove duplicated title from description
# ============================================================

def remove_duplicate_title(
    title,
    description
):

    if not title or not description:
        return description

    title_clean = clean_text(
        title
    )

    desc_clean = clean_text(
        description
    )

    if not title_clean or not desc_clean:
        return desc_clean

    # اگر description با عنوان شروع شده باشد.
    if desc_clean.lower().startswith(
        title_clean.lower()
    ):

        desc_clean = desc_clean[
            len(title_clean):
        ].strip(
            " :-–—|"
        )

    # حذف تکرار عنوان در ابتدای متن.
    desc_clean = re.sub(
        r"^"
        + re.escape(title_clean)
        + r"\s*",
        "",
        desc_clean,
        flags=re.IGNORECASE
    )

    return clean_text(
        desc_clean
    )


# ============================================================
# Sentence splitting
# ============================================================

def split_sentences(text):

    if not text:
        return []

    text = clean_text(
        text
    )

    if not text:
        return []

    # تقسیم تقریبی جملات انگلیسی
    sentences = re.split(
        r"(?<=[.!?])\s+(?=[A-Z0-9])",
        text
    )

    result = []

    for sentence in sentences:

        sentence = clean_text(
            sentence
        )

        if sentence:
            result.append(
                sentence
            )

    return result


# ============================================================
# Detect roundup / multi-story RSS content
# ============================================================

def looks_like_roundup(
    title,
    description
):

    title = clean_text(
        title
    )

    description = clean_text(
        description
    )

    if not description:
        return False

    full_text = (
        title
        + " "
        + description
    ).lower()

    # --------------------------------------------------------
    # 1. عبارات مستقیم roundup
    # --------------------------------------------------------

    for phrase in ROUNDUP_PHRASES:

        if phrase in full_text:
            return True

    # --------------------------------------------------------
    # 2. چند تغییر واضح موضوع
    # --------------------------------------------------------

    shift_count = 0

    for phrase in STORY_SHIFT_PHRASES:

        if phrase in description.lower():
            shift_count += 1

    if shift_count >= 2:
        return True

    # --------------------------------------------------------
    # 3. متن بسیار طولانی با تعداد زیادی جمله
    #
    # یک خبر عادی می‌تواند چند جمله داشته باشد،
    # اما RSS roundup معمولاً تعداد زیادی جمله/موضوع دارد.
    # --------------------------------------------------------

    sentences = split_sentences(
        description
    )

    if len(sentences) >= 6:

        # اگر متن طولانی و چندجمله‌ای است،
        # احتمال تجمیعی بودن آن بیشتر است.
        if len(description) >= 750:
            return True

    # --------------------------------------------------------
    # 4. چند موضوع اقتصادی/سیاسی کاملاً متفاوت
    # --------------------------------------------------------

    topic_groups = {

        "stocks": [
            "stock",
            "stocks",
            "shares",
            "equities",
            "s&p",
            "nasdaq",
            "dow",
        ],

        "fed": [
            "federal reserve",
            "fed ",
            "interest rate",
            "interest rates",
            "rate cut",
            "rate hike",
        ],

        "crypto": [
            "bitcoin",
            "ethereum",
            "crypto",
            "cryptocurrency",
            "token",
            "etf",
        ],

        "geopolitics": [
            "iran",
            "china",
            "russia",
            "ukraine",
            "war",
            "sanctions",
            "tariff",
            "tariffs",
        ],

        "companies": [
            "openai",
            "apple",
            "microsoft",
            "google",
            "amazon",
            "meta",
            "tesla",
        ],

        "oil": [
            "oil",
            "crude",
            "brent",
            "wti",
        ],
    }

    matched_groups = 0

    for keywords in topic_groups.values():

        found = False

        for keyword in keywords:

            if keyword in full_text:
                found = True
                break

        if found:
            matched_groups += 1

    # اگر حداقل 4 حوزه کاملاً متفاوت در یک RSS entry وجود داشته باشد،
    # احتمال roundup بسیار بالاست.
    if matched_groups >= 4:
        return True

    return False


# ============================================================
# Limit text without cutting words
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

    last_space = shortened.rfind(
        " "
    )

    if last_space > limit * 0.75:
        shortened = shortened[
            :last_space
        ]

    return shortened.rstrip(
        " .،؛,:-–—"
    ) + "..."


# ============================================================
# News ID
# ============================================================

def news_id(title):

    normalized = clean_text(
        title
    ).lower()

    return hashlib.md5(
        normalized.encode(
            "utf-8"
        )
    ).hexdigest()


# ============================================================
# Priority
# ============================================================

def check_priority(text):

    if not text:
        return False

    text = text.lower()

    return any(
        word.lower() in text
        for word in URGENT_WORDS
    )


# ============================================================
# Date
# ============================================================

def get_date(item):

    try:

        published = item.get(
            "published_parsed"
        )

        if published:

            return datetime(
                *published[:6],
                tzinfo=timezone.utc
            )

    except Exception:
        pass

    try:

        updated = item.get(
            "updated_parsed"
        )

        if updated:

            return datetime(
                *updated[:6],
                tzinfo=timezone.utc
            )

    except Exception:
        pass

    return datetime.min.replace(
        tzinfo=timezone.utc
    )


# ============================================================
# Recent news
# ============================================================

def is_recent(
    item,
    max_hours=48
):

    published = get_date(
        item
    )

    if published.year == 1:
        return True

    now = datetime.now(
        timezone.utc
    )

    hours = (
        now - published
    ).total_seconds() / 3600

    return (
        0 <= hours <= max_hours
    )


# ============================================================
# Get description
# ============================================================

def get_description(item):

    description = item.get(
        "summary",
        ""
    )

    if not description:

        description = item.get(
            "description",
            ""
        )

    if not description:

        description = item.get(
            "content",
            ""
        )

        if isinstance(
            description,
            list
        ):

            parts = []

            for part in description:

                if isinstance(
                    part,
                    dict
                ):

                    value = part.get(
                        "value",
                        ""
                    )

                    if value:
                        parts.append(
                            value
                        )

            description = " ".join(
                parts
            )

    return clean_text(
        description
    )


# ============================================================
# Get news
# ============================================================

def get_news(
    limit=30
):

    sent = set(
        load_sent()
    )

    news = []

    seen_titles = set()

    for source, url in NEWS_SOURCES.items():

        try:

            feed = feedparser.parse(
                url
            )

            # حداکثر 30 entry از هر منبع بررسی شود.
            for item in feed.entries[:30]:

                # ------------------------------------------
                # Date filter
                # ------------------------------------------

                if not is_recent(
                    item
                ):
                    continue

                # ------------------------------------------
                # Title
                # ------------------------------------------

                title = clean_text(
                    item.get(
                        "title",
                        ""
                    )
                )

                if len(title) < 15:
                    continue

                # ------------------------------------------
                # Duplicate title
                # ------------------------------------------

                normalized_title = re.sub(
                    r"\W+",
                    "",
                    title.lower()
                )

                if normalized_title in seen_titles:
                    continue

                seen_titles.add(
                    normalized_title
                )

                # ------------------------------------------
                # ID
                # ------------------------------------------

                uid = news_id(
                    title
                )

                if uid in sent:
                    continue

                # ------------------------------------------
                # Description
                # ------------------------------------------

                description = get_description(
                    item
                )

                description = remove_rubbish(
                    description
                )

                description = remove_duplicate_title(
                    title,
                    description
                )

                # ------------------------------------------
                # Detect roundup
                # ------------------------------------------

                aggregated = looks_like_roundup(
                    title,
                    description
                )

                # ------------------------------------------
                # Category
                # ------------------------------------------

                category = (
                    "Crypto"
                    if source in CRYPTO_SOURCES
                    else "Market"
                )

                # ------------------------------------------
                # Priority
                #
                # اولویت بر اساس عنوان + متن است،
                # اما در مرحله filter وزن آن کنترل خواهد شد.
                # ------------------------------------------

                urgent = check_priority(
                    title
                )

                # ------------------------------------------
                # News object
                # ------------------------------------------

                news.append({

                    "source": source,

                    "title": title,

                    "description": shorten(
                        description,
                        1200
                    ),

                    "urgent": urgent,

                    "category": category,

                    "aggregated": aggregated,

                    "link": item.get(
                        "link",
                        ""
                    ),

                    "id": uid,

                    "date": get_date(
                        item
                    ),

                })

        except Exception as e:

            print(
                f"⚠️ خطا در دریافت {source}: {e}"
            )

            continue

    # ========================================================
    # مرتب‌سازی اولیه بر اساس تازگی
    # ========================================================

    news.sort(
        key=lambda x: x["date"],
        reverse=True
    )

    # ========================================================
    # حذف کاندیدهای بسیار ضعیف
    #
    # خبرهای aggregated را فعلاً حذف نمی‌کنیم؛
    # به filter می‌فرستیم تا بتواند در امتیازدهی تصمیم بگیرد.
    # ========================================================

    clean_news = []

    for item in news:

        title = item.get(
            "title",
            ""
        )

        description = item.get(
            "description",
            ""
        )

        # عنوان باید معتبر باشد.
        if len(title) < 15:
            continue

        # متن کاملاً خالی قابل قبول است،
        # چون بعضی RSSها description ندارند.
        if description is None:
            item["description"] = ""

        clean_news.append(
            item
        )

    return clean_news[:limit]


# ============================================================
# Test
# ============================================================

if __name__ == "__main__":

    test_title = (
        "Stocks rise before key data as US targets China "
        "with 100% drone tariffs"
    )

    test_description = (
        "US stock futures fluctuated after equities "
        "reached another record ahead of retail sales "
        "and consumer sentiment data. "
        "Treasury Secretary Scott Bessent said the US "
        "would announce unprecedented measures against Iran "
        "next week. "
        "The Trump administration is imposing tariffs "
        "of up to 100% on imported drones and parts. "
        "OpenAI is reportedly on track for more than "
        "$40 billion in annual revenue."
    )

    print(
        "Roundup detected:",
        looks_like_roundup(
            test_title,
            test_description
        )
    )

    print(
        "\nPriority:",
        check_priority(
            test_title
        )
    )
