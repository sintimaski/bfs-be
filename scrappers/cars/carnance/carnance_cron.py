import sys

import os
from loguru import logger

sys.path.append("/root/BFS/")
from app import app
from scrappers.cars.carnance import CarnanceScrapper

logger.add(
    os.path.join(os.getcwd(), "carnance_cron.log"),
    rotation="50 MB",
    format="{time} {level} {message}",
)


@logger.catch
def run():
    if app:
        print("App imported.")
    scrapper = CarnanceScrapper()
    scrapper.start_routine()


if __name__ == "__main__":
    run()
