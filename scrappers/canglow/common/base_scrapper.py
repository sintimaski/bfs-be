import traceback
from concurrent.futures.thread import ThreadPoolExecutor


class BaseCanglowScrapper:
    def __init__(self):
        self.urls = []
        self.data_collected = []

    def start_scrapping(self):
        self.get_urls()
        self.get_data()

    def get_urls(self):
        raise NotImplementedError

    def get_item_wrapper(self, url):
        try:
            data = self.get_item(url)
            return data
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            print(url)
            return {"failed": url}

    def get_item(self, url):
        raise NotImplementedError

    def get_data(self):
        failed = []
        succeed = 0
        passed = 0
        total = len(self.urls)
        with ThreadPoolExecutor(max_workers=8) as executor:
            for item_data in executor.map(self.get_item_wrapper, self.urls):
                passed += 1
                if "failed" not in item_data:
                    succeed += 1
                    self.data_collected.append(item_data)
                else:
                    failed_url = item_data.get("failed", "")
                    # failed.append(failed_url)
                print(f"{succeed}/{passed}/{total}")
        self.urls = failed
        if failed:
            self.get_data()
