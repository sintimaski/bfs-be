def _update_if_exists(_dict, key, value):
    if key in _dict:
        _dict.update(
            {
                key: value,
            }
        )


def adjust_car_data(car_data):
    if "fuel" in car_data:
        fuel = car_data["fuel"].lower()
        if "diesel" not in fuel and "electric" not in fuel:
            fuel = "Gas"
        else:
            fuel = car_data["fuel"]
        _update_if_exists(car_data, "fuel", fuel)

    if "body_type" in car_data:
        body_type = car_data["body_type"]
        if body_type == "Sport Utility Vehicle":
            body_type = "SUV"
        _update_if_exists(car_data, "body_type", body_type)

    if "transmission" in car_data:
        transmission = car_data["transmission"].lower()
        if "cvt" in transmission or "automatic" in transmission:
            transmission = "Automatic"
        else:
            transmission = "Manual"
        _update_if_exists(car_data, "transmission", transmission)

    if "driveline" in car_data:
        driveline = car_data["driveline"]
        driveline = driveline.lower()
        driveline = driveline.replace("-", " ")
        driveline_mapper = {
            "four wheel drive": "AWD",
            "front wheel drive": "FWD",
            "all wheel drive": "AWD",
            "rear wheel Drive": "RWD",
            "quattro": "AWD",
        }
        driveline = driveline_mapper.get(driveline, car_data["driveline"])
        _update_if_exists(car_data, "driveline", driveline)
    return car_data


def filter_value(value):
    if isinstance(value, str):
        to_delete = ["-", "null", "None"]
        value = value if value not in to_delete else ""
        value = value.strip()
    return value


def _convert_odometer(mileage: str):
    mileage = 235.21 / int(mileage.split(" ", 1)[0])
    mileage = int(mileage)
    converted = f"{mileage}L/100Km"
    return converted


def get_element_text(soup, selector) -> str:
    tag = soup.select_one(selector)
    text = tag.text if tag else ""
    text = text.strip()
    if text == "null" or text is None:
        text = ""
    return text


def find_between(s, first, last) -> str:
    try:
        start = s.index(first) + len(first)
        end = s.index(last, start)
        return s[start:end]
    except ValueError:
        return ""


# MOVE TO SCRAPPERS.CARS.COMMON
# import csv
# from scrappers.cars.autoloancentre import AutoLoanCentreScrapper
# scrapper = AutoLoanCentreScrapper()
# formatted = scrapper.get_formatted_cars()
# with open("cars.csv", "w+") as file:
#     fieldnames = list(formatted[0].keys())
#     fieldnames.extend(
#       ['seatingNum', 'carMileage', 'airbagNum', 'doorsNum']
#     )
#     writer = csv.DictWriter(
#         file, fieldnames=fieldnames, quoting=csv.QUOTE_ALL
#     )
#     writer.writeheader()
#     writer.writerows(formatted)
