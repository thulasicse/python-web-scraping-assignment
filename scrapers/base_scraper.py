import logging
import time

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry


logger = logging.getLogger(__name__)


class BaseScraper:
    def __init__(self, delay=0.5, timeout=10):
        self.delay = delay
        self.timeout = timeout

        self.session = requests.Session()

        self.session.headers.update({
            "User-Agent": "RealizeTechnologiesAssignment/1.0"
        })

        retries = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"]
        )

        adapter = HTTPAdapter(max_retries=retries)

        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def fetch(self, url):
        logger.info("Fetching URL: %s", url)

        response = self.session.get(
            url,
            timeout=self.timeout
        )

        response.raise_for_status()

        response.encoding = "utf-8"

        time.sleep(self.delay)

        return response