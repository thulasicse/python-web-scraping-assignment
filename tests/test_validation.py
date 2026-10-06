from processing.validation import validate_record


def test_valid_record():
    record = {
        "source": "Books to Scrape",
        "source_url": "https://books.toscrape.com/",
        "name_or_title": "Example Book",
        "price": 10.50,
        "rating": 4
    }

    assert validate_record(record) == []


def test_missing_name():
    record = {
        "source": "Books to Scrape",
        "source_url": "https://books.toscrape.com/",
        "name_or_title": None,
        "price": 10.50,
        "rating": 4
    }

    problems = validate_record(record)

    assert "missing_name" in problems


def test_invalid_rating():
    record = {
        "source": "Books to Scrape",
        "source_url": "https://books.toscrape.com/",
        "name_or_title": "Example",
        "price": 10.50,
        "rating": 8
    }

    problems = validate_record(record)

    assert "invalid_rating" in problems