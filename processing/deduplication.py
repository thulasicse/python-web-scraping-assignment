import hashlib
import re


def normalize_for_fingerprint(value):
    value = str(value or "")

    value = value.lower()

    value = re.sub(
        r"[^\w\s]",
        "",
        value
    )

    value = " ".join(value.split())

    return value


def make_fingerprint(record):
    source = normalize_for_fingerprint(
        record.get("source")
    )

    name = normalize_for_fingerprint(
        record.get("name_or_title")
    )

    if record.get("source") == "Books to Scrape":
        key = f"{source}|{name}"

    else:
        author = normalize_for_fingerprint(
            record.get("author")
        )

        quote = name[:50]

        key = f"{source}|{author}|{quote}"

    return hashlib.sha256(
        key.encode("utf-8")
    ).hexdigest()


def find_duplicates(records):
    seen = set()
    unique_records = []
    duplicate_records = []

    for record in records:
        fingerprint = make_fingerprint(record)

        if fingerprint in seen:
            duplicate_records.append(record)
        else:
            seen.add(fingerprint)
            unique_records.append(record)

    return unique_records, duplicate_records