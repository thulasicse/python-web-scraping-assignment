import logging
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from scrapers.base_scraper import BaseScraper


logger = logging.getLogger(__name__)


class BooksScraper(BaseScraper):
    BASE_URL = "https://books.toscrape.com/"

    def scrape(self):
        records = []
        url = self.BASE_URL
        page_number = 1

        while url:
            logger.info(
                "Books to Scrape - page %d: %s",
                page_number,
                url
            )

            try:
                response = self.fetch(url)
            except Exception as exc:
                logger.error(
                    "Books page failed: %s | Error: %s",
                    url,
                    exc
                )
                break

            soup = BeautifulSoup(response.text, "lxml")

            books = soup.select("article.product_pod")

            for book in books:
                try:
                    record = self.parse_book(book, url)
                    records.append(record)
                except Exception as exc:
                    logger.warning(
                        "Failed to parse a book: %s",
                        exc
                    )

            next_link = soup.select_one("li.next > a")

            if next_link and next_link.get("href"):
                url = urljoin(url, next_link["href"])
                page_number += 1
            else:
                url = None

        logger.info(
            "Books scraping completed. Records collected: %d",
            len(records)
        )

        return records

    def parse_book(self, book, page_url):
        title_element = book.select_one("h3 > a")
        price_element = book.select_one("p.price_color")
        rating_element = book.select_one("p.star-rating")

        title = (
            title_element.get("title")
            if title_element
            else None
        )

        href = (
            urljoin(page_url, title_element.get("href"))
            if title_element and title_element.get("href")
            else None
        )

        price = (
            price_element.get_text()
            if price_element
            else None
        )

        rating = (
            " ".join(rating_element.get("class", []))
            if rating_element
            else None
        )

        return {
            "source": "Books to Scrape",
            "source_url": href,
            "name_or_title": title,
            "category": None,
            "price": price,
            "rating": rating,
            "author": None,
            "tags": None,
            "description": None
        }