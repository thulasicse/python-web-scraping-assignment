from processing.deduplication import find_duplicates


def test_duplicates_ignore_case_and_spaces():
    records = [
        {
            "source": "Books to Scrape",
            "name_or_title": "Example Book Title"
        },
        {
            "source": "Books to Scrape",
            "name_or_title": "  Example Book Title "
        },
        {
            "source": "Books to Scrape",
            "name_or_title": "EXAMPLE BOOK TITLE"
        }
    ]

    unique, duplicates = find_duplicates(records)

    assert len(unique) == 1
    assert len(duplicates) == 2