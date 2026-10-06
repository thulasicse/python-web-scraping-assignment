import re
from urllib.parse import urljoin


RATING_MAP = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5
}


def clean_text(value):
    if value is None:
        return None

    value = value.replace("\xa0", " ")

    value = " ".join(value.split())

    return value or None


def strip_quotes(value):
    value = clean_text(value)

    if not value:
        return None

    return value.strip("“”\"")


def clean_price(value):
    if value is None:
        return None

    match = re.search(
        r"\d+(?:\.\d+)?",
        value.replace(",", "")
    )

    if not match:
        return None

    return float(match.group())


def clean_rating(value):
    if not value:
        return None

    for word in value.lower().split():
        if word in RATING_MAP:
            return RATING_MAP[word]

    return None


def clean_tags(tags):
    if not tags:
        return None

    cleaned = []

    for tag in tags:
        tag = clean_text(str(tag))

        if tag:
            cleaned.append(tag.lower())

    cleaned = sorted(set(cleaned))

    return ";".join(cleaned) if cleaned else None


def normalize_url(value, base_url=None):
    if not value:
        return None

    value = clean_text(value)

    if base_url:
        value = urljoin(base_url, value)

    if value.startswith(("http://", "https://")):
        return value

    return None


def clean_record(record):
    cleaned = dict(record)

    cleaned["source"] = clean_text(cleaned.get("source"))

    cleaned["source_url"] = normalize_url(
        cleaned.get("source_url")
    )

    cleaned["name_or_title"] = clean_text(
        cleaned.get("name_or_title")
    )

    if cleaned.get("source") == "Quotes to Scrape":
        cleaned["name_or_title"] = strip_quotes(
            cleaned.get("name_or_title")
        )

    cleaned["category"] = clean_text(
        cleaned.get("category")
    )

    cleaned["price"] = clean_price(
        cleaned.get("price")
    )

    cleaned["rating"] = clean_rating(
        cleaned.get("rating")
    )

    cleaned["author"] = clean_text(
        cleaned.get("author")
    )

    cleaned["tags"] = clean_tags(
        cleaned.get("tags")
    )

    cleaned["description"] = clean_text(
        cleaned.get("description")
    )

    return cleaned