import requests
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

API_KEY = "c7eaa70b717984c24bf57e5ba68fb7d9"


class Weather:
    def read_weather(self, city):
        logger.info(f"Rozpoczynam pobieranie pogody dla miasta: {city}")
        try:
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}"
            req = requests.get(url)
            req.raise_for_status()
            data = req.json()

            name = data["name"]
            lon = data["coord"]["lon"]
            lat = data["coord"]["lat"]
            logger.info(
                f"Znaleziono miasto: {name}, długość geograficzna: {lon}, szerokość geograficzna: {lat}"
            )

            forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&cnt=40&units=metric&appid={API_KEY}"
            req = requests.get(forecast_url)
            req.raise_for_status()
            forecast_data = req.json()

            logger.info("Pogoda została pomyślnie pobrana.")
            return forecast_data

        except requests.exceptions.HTTPError as http_err:
            logger.error(f"Wystąpił błąd HTTP: {http_err}")
        except Exception as err:
            logger.error(f"Wystąpił błąd: {err}")


# if __name__ == "__main__":
#     db = Weather()
#     data = db.read_weather("Warsaw")
#     print(data)
