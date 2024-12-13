from database import Database
from weather import Weather
from datetime import datetime
import logging
import coloredlogs

coloredlogs.DEFAULT_LEVEL_STYLES = {
    "error": {
        "color": "red",
    },
    "info": {"color": "blue"},
    "warning": {"color": "yellow"},
}

coloredlogs.DEFAULT_FIELD_STYLES = {
    "asctime": {"color": "green"},
    "filename": {"color": "blue"},
    "levelname": {"bold": True},
    "message": {},
}

coloredlogs.DEFAULT_LOG_FORMAT = (
    "%(asctime)s - %(filename)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)
coloredlogs.install(level=logging.INFO, logger=logger)


class Controller:
    def __init__(self):
        self.database = Database()
        self.weather = Weather()

    def process(self, city):
        cityTable = self.database.get_tables()

        if city in cityTable:
            existing_records = self.database.fetch_records(city)
            existing_dates = {record[0] for record in existing_records}

        else:
            self.database.create_table(city)
            existing_dates = set()

        data = self.weather.read_weather(city)

        if data and "list" in data:
            for entry in data["list"]:
                timestamp = entry["dt"]
                temp = entry["main"]["temp"]
                perceived_temp = entry["main"].get("feels_like")
                humidity = entry["main"]["humidity"]
                pressure = entry["main"]["pressure"]
                date_time = datetime.fromtimestamp(timestamp).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

                if date_time not in existing_dates:
                    self.database.insert_record(
                        city, date_time, temp, perceived_temp, humidity, pressure
                    )
                    logger.info(
                        f"Dane pogodowe dla {city} w dniu {date_time} zostały zapisane w bazie."
                    )
                else:
                    logger.info(
                        f"Dane dla {city} w dniu {date_time} już istnieją, pomijam zapis."
                    )

        weather = self.database.fetch_records(city)
        return weather

    def close(self):
        self.database.close()

    def fetch_records(self, city_name):
        records = self.database.fetch_records(city_name)
        return records


# if __name__ == "__main__":
#     controller = Controller()
#     data = controller.process("moscow")
#     controller.close()
