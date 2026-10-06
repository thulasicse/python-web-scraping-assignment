import csv
import json
import logging
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from processing.cleaning import clean_record
from processing.deduplication import find_duplicates
from processing.validation import validate_record
from scrapers.books_scraper import BooksScraper
from scrapers.quotes_scraper import QuotesScraper


BASE_DIR = Path(__file__).resolve().parent

OUTPUT_DIR = BASE_DIR / "output"
LOG_DIR = BASE_DIR / "logs"

CSV_PATH = OUTPUT_DIR / "final_dataset.csv"
SUMMARY_PATH = OUTPUT_DIR / "summary_report.json"
LOG_PATH = LOG_DIR / "scraper.log"


CSV_FIELDS = [
    "source",
    "source_url",
    "name_or_title",
    "category",
    "price",
    "rating",
    "author",
    "tags",
    "description",
    "scraped_at"
]


def setup_logging():
    LOG_DIR.mkdir(exist_ok=True)

    logger = logging.getLogger()

    logger.setLevel(logging.INFO)

    logger.handlers.clear()

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )

    file_handler = logging.FileHandler(
        LOG_PATH,
        encoding="utf-8"
    )

    console_handler = logging.StreamHandler()

    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


def add_timestamp(record):
    record = dict(record)

    record["scraped_at"] = datetime.now(
        timezone.utc
    ).isoformat()

    return record


def process_records(raw_records, source_name):
    cleaned_records = []
    rejected_reasons = Counter()

    for raw_record in raw_records:
        try:
            cleaned = clean_record(raw_record)

            problems = validate_record(cleaned)

            if problems:
                for problem in problems:
                    rejected_reasons[problem] += 1

                logging.warning(
                    "Rejected record from %s: %s",
                    source_name,
                    problems
                )

                continue

            cleaned = add_timestamp(cleaned)

            cleaned_records.append(cleaned)

        except Exception as exc:
            rejected_reasons["processing_error"] += 1

            logging.warning(
                "Record processing failed from %s: %s",
                source_name,
                exc
            )

    return cleaned_records, rejected_reasons


def write_csv(records):
    OUTPUT_DIR.mkdir(exist_ok=True)

    with open(
        CSV_PATH,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=CSV_FIELDS
        )

        writer.writeheader()

        writer.writerows(records)


def write_summary(summary):
    OUTPUT_DIR.mkdir(exist_ok=True)

    with open(
        SUMMARY_PATH,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            summary,
            file,
            indent=4
        )


def main():
    setup_logging()

    logger = logging.getLogger(__name__)

    start_time = time.time()

    start_datetime = datetime.now(
        timezone.utc
    ).isoformat()

    logger.info("Scraping pipeline started")

    raw_by_source = {}
    cleaned_by_source = {}
    rejected_by_source = {}

    # -------------------------
    # BOOKS
    # -------------------------

    try:
        books_scraper = BooksScraper()

        raw_books = books_scraper.scrape()

        raw_by_source["Books to Scrape"] = raw_books

        cleaned_books, rejected_books = process_records(
            raw_books,
            "Books to Scrape"
        )

        cleaned_by_source["Books to Scrape"] = cleaned_books

        rejected_by_source["Books to Scrape"] = dict(
            rejected_books
        )

    except Exception as exc:
        logger.error(
            "Books source failed completely: %s",
            exc
        )

        raw_by_source["Books to Scrape"] = []
        cleaned_by_source["Books to Scrape"] = []
        rejected_by_source["Books to Scrape"] = {
            "source_failure": 1
        }

    # -------------------------
    # QUOTES
    # -------------------------

    try:
        quotes_scraper = QuotesScraper()

        raw_quotes = quotes_scraper.scrape()

        raw_by_source["Quotes to Scrape"] = raw_quotes

        cleaned_quotes, rejected_quotes = process_records(
            raw_quotes,
            "Quotes to Scrape"
        )

        cleaned_by_source["Quotes to Scrape"] = cleaned_quotes

        rejected_by_source["Quotes to Scrape"] = dict(
            rejected_quotes
        )

    except Exception as exc:
        logger.error(
            "Quotes source failed completely: %s",
            exc
        )

        raw_by_source["Quotes to Scrape"] = []
        cleaned_by_source["Quotes to Scrape"] = []
        rejected_by_source["Quotes to Scrape"] = {
            "source_failure": 1
        }

    # -------------------------
    # CONSOLIDATE
    # -------------------------

    all_cleaned_records = (
        cleaned_by_source["Books to Scrape"]
        + cleaned_by_source["Quotes to Scrape"]
    )

    unique_records, duplicate_records = find_duplicates(
        all_cleaned_records
    )

    for record in duplicate_records:
        logger.warning(
            "Duplicate removed: %s",
            record.get("name_or_title")
        )

    write_csv(unique_records)

    end_datetime = datetime.now(
        timezone.utc
    ).isoformat()

    duration = round(
        time.time() - start_time,
        2
    )

    summary = {
        "start_time_utc": start_datetime,
        "end_time_utc": end_datetime,
        "duration_seconds": duration,

        "collected_per_source": {
            source: len(records)
            for source, records
            in raw_by_source.items()
        },

        "cleaned_per_source": {
            source: len(records)
            for source, records
            in cleaned_by_source.items()
        },

        "rejected_by_source": rejected_by_source,

        "duplicates_detected": len(
            duplicate_records
        ),

        "final_record_count": len(
            unique_records
        )
    }

    write_summary(summary)

    logger.info(
        "Pipeline completed successfully"
    )

    logger.info(
        "Final records: %d",
        len(unique_records)
    )

    logger.info(
        "Output CSV: %s",
        CSV_PATH
    )

    logger.info(
        "Summary report: %s",
        SUMMARY_PATH
    )


if __name__ == "__main__":
    main()