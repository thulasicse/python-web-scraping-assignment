import logging
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from scrapers.base_scraper import BaseScraper


logger = logging.getLogger(__name__)


class QuotesScraper(BaseScraper):
    BASE_URL = "https://quotes.toscrape.com/"

    def scrape(self):
        records = []
        url = self.BASE_URL
        page_number = 1

        while url:
            logger.info(
                "Quotes to Scrape - page %d: %s",
                page_number,
                url
            )

            try:
                response = self.fetch(url)
            except Exception as exc:
                logger.error(
                    "Quotes page failed: %s | Error: %s",
                    url,
                    exc
                )
                break

            soup = BeautifulSoup(response.text, "lxml")

            quotes = soup.select("div.quote")

            for quote in quotes:
                try:
                    record = self.parse_quote(quote, url)
                    records.append(record)
                except Exception as exc:
                    logger.warning(
                        "Failed to parse a quote: %s",
                        exc
                    )

            next_link = soup.select_one("li.next > a")

            if next_link and next_link.get("href"):
                url = urljoin(url, next_link["href"])
                page_number += 1
            else:
                url = None

        logger.info(
            "Quotes scraping completed. Records collected: %d",
            len(records)
        )

        return records

    def parse_quote(self, quote, page_url):
        text_element = quote.select_one("span.text")
        author_element = quote.select_one("small.author")

        text = (
            text_element.get_text()
            if text_element
            else None
        )

        author = (
            author_element.get_text()
            if author_element
            else None
        )

        tags = [
            tag.get_text()
            for tag in quote.select("a.tag")
        ]

        author_link = quote.select_one('a[href^="/author/"]')

        source_url = page_url

        if author_link and author_link.get("href"):
            source_url = urljoin(
                page_url,
                author_link.get("href")
            )

        return {
            "source": "Quotes to Scrape",
            "source_url": source_url,
            "name_or_title": text,
            "category": "Quotes",
            "price": None,
            "rating": None,
            "author": author,
            "tags": tags,
            "description": None
        }