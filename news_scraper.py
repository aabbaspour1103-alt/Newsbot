import feedparser
import hashlib
import html
import json
import os
import re
from datetime import datetime, timezone


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


URGENT_WORDS = [
    "Trump",
    "Donald Trump",
    "Federal Reserve",
    "Fed",
    "interest rate",
    "rate cut",
    "rate hike",
    "Bitcoin ETF",
    "ETF",
    "SEC",
    "hack",
    "hacked",
    "data breach",
    "crash",
    "war",
    "sanctions",
    "breaking",
    "emergency",
    "approval",
    "ban",
    "regulation",
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


# --------------------------------------------------
# Sent news
# --------------------------------------------------

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
        # فقط 1000 خبر آخر نگهداری شود
        data = list(dict.fromkeys(data))

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

    news_id_value = news_item.get("id")

    if not news_id_value:
        return

    if news_id_value not in sent:
        sent.append(news_id_value)

    save_sent(sent)


# --------------------------------------------------
# Text cleaning
# --------------------------------------------------

def clean_text(text):

    if not text:
        return ""

    # تبدیل HTML entity ها
    # مثل:
    # &#160;
    # &nbsp;
    # &amp;
    text = html.unescape(str(text))

    # حذف تگ‌های HTML
    text = re.sub(
        r"<[^>]+>",
        " ",
        text
    )

    # حذف URLهای اضافی داخل description
    text = re.sub(
        r"https?://\S+",
        " ",
        text
    )

    # حذف entityهایی که ممکن است باقی مانده باشند
    text = re.sub(
        r"&[a-zA-Z0-9#]+;",
        " ",
        text
    )

    # تبدیل خط‌های جدید و tab به فاصله
    text = re.sub(
        r"[\r\n\t]+",
        " ",
        text
    )

    # حذف فاصله‌های چندتایی
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# --------------------------------------------------
# Remove RSS / website rubbish
# --------------------------------------------------

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


# --------------------------------------------------
# Remove duplicated title from description
# --------------------------------------------------

def remove_duplicate_title(title, description):

    if not title or not description:
        return description

    title_clean = clean_text(title)
    desc_clean = clean_text(description)

    if not title_clean or not desc_clean:
        return desc_clean

    # اگر description با عنوان شروع شده باشد
    if desc_clean.lower().startswith(
        title_clean.lower()
    ):

        desc_clean = desc_clean[
            len(title_clean):
        ].strip(" :-–—|")

    # اگر عنوان چند بار پشت سر هم آمده باشد
    desc_clean = re.sub(
        r"^" + re.escape(title_clean) + r"\s*",
        "",
        desc_clean,
        flags=re.IGNORECASE
    )

    return clean_text(desc_clean)


# --------------------------------------------------
# Limit text without cutting words
# --------------------------------------------------

def shorten(text, limit=500):

    if not text:
        return ""

    text = clean_text(text)

    if len(text) <= limit:
        return text

    shortened = text[:limit]

    # در وسط کلمه قطع نکن
    last_space = shortened.rfind(" ")

    if last_space > limit * 0.75:
        shortened = shortened[:last_space]

    return shortened.rstrip(
        " .،؛,:-–—"
    ) + "..."


# --------------------------------------------------
# News ID
# --------------------------------------------------

def news_id(title):

    normalized = clean_text(title).lower()

    return hashlib.md5(
        normalized.encode("utf-8")
    ).hexdigest()


# --------------------------------------------------
# Priority
# --------------------------------------------------

def check_priority(text):

    if not text:
        return False

    text = text.lower()

    return any(
        word.lower() in text
        for word in URGENT_WORDS
    )


# --------------------------------------------------
# Date
# --------------------------------------------------

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


# --------------------------------------------------
# Recent news
# --------------------------------------------------

def is_recent(item, max_hours=48):

    published = get_date(item)

    if published.year == 1:
        return True

    now = datetime.now(
        timezone.utc
    )

    hours = (
        now - published
    ).total_seconds() / 3600

    return 0 <= hours <= max_hours


# --------------------------------------------------
# Get description
# --------------------------------------------------

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
                        parts.append(value)

            description = " ".join(parts)

    return clean_text(
        description
    )


# --------------------------------------------------
# Get news
# --------------------------------------------------

def get_news(limit=30):

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

            for item in feed.entries[:30]:

                # ----------------------------------
                # Date filter
                # ----------------------------------

                if not is_recent(item):
                    continue

                # ----------------------------------
                # Title
                # ----------------------------------

                title = clean_text(
                    item.get(
                        "title",
                        ""
                    )
                )

                if len(title) < 15:
                    continue

                # ----------------------------------
                # Duplicate title
                # ----------------------------------

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

                # ----------------------------------
                # ID
                # ----------------------------------

                uid = news_id(
                    title
                )

                if uid in sent:
                    continue

                # ----------------------------------
                # Description
                # ----------------------------------

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

                description = shorten(
                    description,
                    500
                )

                # ----------------------------------
                # Category
                # ----------------------------------

                category = (
                    "Crypto"
                    if source in CRYPTO_SOURCES
                    else "Market"
                )

                # ----------------------------------
                # Priority
                # ----------------------------------

                urgent = check_priority(
                    title + " " + description
                )

                # ----------------------------------
                # News object
                # ----------------------------------

                news.append({

                    "source": source,

                    "title": title,

                    "description": description,

                    "urgent": urgent,

                    "category": category,

                    "link": item.get(
                        "link",
                        ""
                    ),

                    "id": uid,

                    "date": get_date(
                        item
                    ),

                })

        except Exception:
            continue

    # --------------------------------------
    # مرتب‌سازی اولیه بر اساس تازگی
    # --------------------------------------

    news.sort(
        key=lambda x: x["date"],
        reverse=True
    )

    # --------------------------------------
    # فقط کاندیدها را برگردان
    # --------------------------------------

    return news[:limit]
