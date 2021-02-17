import json
import traceback

import cloudscraper

from scrappers.cars.common.base_scrapper import BaseCarScrapper


class OrillaVWScrapper(BaseCarScrapper):
    def __init__(self, project):
        source = "orilliavw"
        self.all_vehicles = []
        self.current = 0
        super().__init__(source, project)

    def get_dealership_data(self, car_url: str):
        try:
            vehicle = self.all_vehicles[self.current]
            odometer = (
                "".join(
                    [
                        n
                        for n in vehicle.get("odometer_value", "")
                        if str(n).isnumeric()
                    ]
                )
                or None
            )
            if odometer:
                odometer = int(odometer)

            specifications = vehicle.get("specifications", {})

            fuel = specifications.get("Fuel Economy", {})
            city = fuel.get("Fuel Economy - city (L/100 km)", "")
            if city:
                city = f"{city}L/100Km"
            hwy = fuel.get("Fuel Economy - highway (L/100 km)", "")
            if hwy:
                hwy = f"{hwy}L/100Km"

            engine_size = vehicle.get("engine", {}).get("litres", "")
            engine_size = f"{engine_size} L"

            car_data = {
                "source": self.source,
                "trim": vehicle.get("trim", {}).get("description", ""),
                "condition": vehicle.get("stock_type", ""),
                "price": vehicle.get("pricingData", {}).get("current", ""),
                "images": vehicle.get("photos", {}).get("user", []),
                "make": vehicle.get("make", ""),
                "model": vehicle.get("model", ""),
                "year": vehicle.get("year", None),
                "body_type": vehicle.get("body_type", ""),
                "odometer": odometer,
                "transmission": vehicle.get("transmission", ""),
                "engine": vehicle.get("engine_combined", ""),
                "engine_size": engine_size,
                "driveline": vehicle.get("driveType", ""),
                "exterior_color": vehicle.get("color_exterior", ""),
                "interior_color": vehicle.get("color", {}).get("interior", {}).get("generic", ""),
                "doors": vehicle.get("doors", ""),
                "fuel": vehicle.get("engine", {}).get("fuel_type", ""),
                "city_fuel": city,
                "hwy_fuel": hwy,
                "stock_number": vehicle.get("stock_number", ""),
                "vin": vehicle.get("vin", ""),
                "details": vehicle.get("description", ""),
            }
            self.current += 1
            return car_data
        except Exception as e:
            print(traceback.format_exc())
            return {"failed": car_url}

    def get_cars_urls(self):
        listing_url = "https://www.orilliavw.ca/wp-json/strathcom/vehicles/search?page={}&page_length={}&sort_by=price"
        page = 1
        page_length = 10
        while True:
            scraper = cloudscraper.create_scraper()
            resp = scraper.get(
                listing_url.format(page, page_length), timeout=120
            )
            data = json.loads(resp.text)["data"]
            vehicles = data["vehicles"]
            if not vehicles:
                break
            for item in vehicles:
                self.cars_urls.append(item["vin"])
                self.all_vehicles.append(item)
            page += 1
