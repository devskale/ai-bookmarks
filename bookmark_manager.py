import gevent
from gevent import monkey

monkey.patch_all()

from bs4 import BeautifulSoup
import csv
from bookmark import Bookmark


class BookmarkManager:
    def __init__(self):
        self.bookmarks = []

    def load(self, source):
        soup = BeautifulSoup(source, "html.parser")
        Atags = soup.find_all("a")
        for i in Atags:
            url = i.get("href", "")
            add_date = i.get("add_date", "")
            icon = i.get("icon", "")
            bookmark = Bookmark(url, add_date, icon)
            self.bookmarks.append(bookmark)

    def retrieve(self):
        tasks = [gevent.spawn(bookmark.retrieve) for bookmark in self.bookmarks]
        results = gevent.joinall(tasks)
        for result in results:
            print("Completed access", result.value)

    def export(self, file_name):
        with open(file_name, "w") as csvfile:
            fieldnames = ["url", "title", "description", "date", "icon"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for bookmark in self.bookmarks:
                if bookmark.title != "" and bookmark.description != "":
                    writer.writerow(bookmark.export())
            print("Done")

    def export_failed(self, file_name):
        with open(file_name, "w") as csvfile:
            fieldnames = ["url", "title", "description", "date", "icon"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for bookmark in self.bookmarks:
                if bookmark.title == "" or bookmark.description == "":
                    writer.writerow(bookmark.export())
            print("Done")
