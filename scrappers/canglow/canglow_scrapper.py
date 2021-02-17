import csv
import unicodedata

import os

from . import (
    FusionGlassScrapper,
    GroupeNovaTechScrapper,
    MennieCanadaScrapper,
    OdlScrapper,
    TrimliteScrapper,
)


class CanglowScrapper:
    def __init__(self):
        self.scrappers = [
            TrimliteScrapper,
            FusionGlassScrapper,
            GroupeNovaTechScrapper,
            MennieCanadaScrapper,
            OdlScrapper,
        ]
        self.data_collected = []

    def start_routine(self):
        self.collect_data()
        self.format_data()
        self.export_to_file()

    def collect_data(self):
        for _scrapper in self.scrappers:
            scrapper = _scrapper()
            scrapper.start_scrapping()
            self.data_collected.extend(scrapper.data_collected)
            print(f"{_scrapper.__name__} Done")

    def format_data(self):
        result = []
        for item in self.data_collected:
            res = {}
            for key, value in item.items():
                if isinstance(value, list):
                    value = "|".join(value)
                value = str(value)

                value = (
                    unicodedata.normalize("NFD", value)
                    .encode("ascii", "ignore")
                    .decode("ascii")
                    .strip()
                )

                res.update({key: value})
            result.append(res)
        self.data_collected = result

    def export_to_file(self):
        _keys = []
        for item in self.data_collected:
            for key, values in list(item.items()):
                if key not in _keys:
                    _keys.append(key)

        filename = "canglow_data.csv"
        dir_path = os.path.dirname(os.path.realpath(__file__))
        filepath = os.path.join(dir_path, filename)
        with open(filepath, "w+") as file:
            fieldnames = list(_keys)
            writer = csv.DictWriter(
                file, fieldnames=fieldnames, quoting=csv.QUOTE_ALL
            )
            writer.writeheader()
            writer.writerows(self.data_collected)

    # def format_data(self):
    #     # result = []
    #     # for item in self.data_collected:
    #     #     item.update({
    #     #         "images": "|".join(item['images']),
    #     #         "alts": "|".join(item['alts']),
    #     #     })
    #     #     result.append(item)
    #     _keys = []
    #     filename = "canglow_data.csv"
    #     dir_path = os.path.dirname(os.path.realpath(__file__))
    #     filepath = os.path.join(dir_path, filename)
    #
    #     result = []
    #     with open(os.path.join(dir_path, "canglow_data2.csv"), "r") as file:
    #         reader = csv.DictReader(file, quoting=csv.QUOTE_ALL)
    #         for line in reader:
    #             line["images"] = line["images"].replace("['", "")
    #             line["images"] = line["images"].replace("']", "")
    #             line["images"] = line["images"].replace("', '", "|")
    #
    #             line["alts"] = line["alts"].replace("['", "")
    #             line["alts"] = line["alts"].replace("']", "")
    #             line["alts"] = line["alts"].replace("', '", "|")
    #
    #             res = {}
    #             print(line["description"].encode("utf-8"))
    #             print(
    #                 bytes(line["description"], encoding="utf8").decode("utf8")
    #             )
    #             for key, value in line.items():
    #                 value = bytes(value).decode("WINDOWS-1251")
    #                 res.update(
    #                     {
    #                         key: value,
    #                     }
    #                 )
    #             result.append(res)
    #
    #     for item in result:
    #         for key in list(item.keys()):
    #             if key not in _keys:
    #                 _keys.append(key)
    #     with open(filepath, "w+") as file:
    #         fieldnames = list(_keys)
    #         writer = csv.DictWriter(
    #             file, fieldnames=fieldnames, quoting=csv.QUOTE_ALL
    #         )
    #         writer.writeheader()
    #         writer.writerows(result)
