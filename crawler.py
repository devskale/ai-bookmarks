import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

from parser import Parser  # Ensure this is your custom parser module
from bookmark import Bookmark  # Ensure this matches your Bookmark class
# Ensure this matches your BookmarkManager class
from bookmark_manager import BookmarkManager


class Crawler:
    def __init__(self, manager: BookmarkManager):
        self.manager = manager
        self.num_retrievers = 20  # Number of parallel retrievers

    def parse(self, file_name: str):
        """Parse bookmarks from an HTML file and add them to the manager."""
        with open(file_name, "r") as file:
            document = file.read()
        soup = BeautifulSoup(document, "html.parser")
        a_tags = soup.find_all("a")
        for tag in a_tags:
            url = tag.get("href", "")
            if self.is_valid_url(url):  # Ensure URL is valid before processing
                add_date = tag.get("add_date", "")
                icon = tag.get("icon", "")
                bookmark = Bookmark(url, date=add_date, icon=icon)
                self.manager.add(bookmark)

    def retrieve(self):
        """Retrieve bookmarks in parallel."""
        valid_bookmarks = [
            bookmark for bookmark in self.manager.bookmarks if self.is_valid_url(bookmark.url)]
        total = len(valid_bookmarks)  # Total number of valid bookmarks

        with ThreadPoolExecutor(max_workers=self.num_retrievers) as executor:
            # Create a future for each bookmark retrieval
            future_to_bookmark = {executor.submit(
                self.retrieveBookmark, bookmark, num+1, total): bookmark for num, bookmark in enumerate(valid_bookmarks)}

            for future in as_completed(future_to_bookmark):
                bookmark = future_to_bookmark[future]
                try:
                    future.result()  # Retrieve the result to handle exceptions
                except Exception as exc:
                    print(f"Bookmark retrieval failed for "
                          f"{bookmark.url}: {exc}")
        print("Completed")

    def crawl(self, url: str, timeout=4):
        """Fetch the webpage content for a given URL."""
        try:
            response = requests.get(url, timeout=timeout)
            response.encoding = "utf-8"
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching URL {url}: {e}")
            return None

    def retrieveBookmark(self, bookmark: Bookmark, num: int, total: int):
        """Retrieve and parse bookmark information with progress indication."""
        percentage = (num / total) * \
            100  # Calculate the percentage of progress
        print(f"{percentage:.2f}% ({num}/{total}). Accessing {bookmark.url}")
        html_content = self.crawl(bookmark.url)
        if html_content:
            parser = Parser(html_content)
            bookmark.title = parser.get_title()
            bookmark.description = parser.get_description()

    def is_valid_url(self, url):
        """Check if the URL has a valid HTTP/HTTPS scheme and is not from blocked domains or schemes."""
        parsed_url = urlparse(url)
        valid_scheme = parsed_url.scheme in ['http', 'https']
        blocked_domains = ['drive.google.com']
        blocked_schemes = ['chrome']
        domain_blocked = any(
            blocked_domain in parsed_url.netloc for blocked_domain in blocked_domains)
        scheme_blocked = parsed_url.scheme in blocked_schemes
        return valid_scheme and not domain_blocked and not scheme_blocked
