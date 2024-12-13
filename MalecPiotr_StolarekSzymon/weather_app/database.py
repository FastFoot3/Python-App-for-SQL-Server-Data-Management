import mysql.connector
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


class Database:
    def __init__(self):
        self._connect()

    def _connect(self):
        try:
            self.connection = mysql.connector.connect(
                host="localhost", user="root", password="1234", database="weather"
            )
            self.cursor = self.connection.cursor()
            logger.info("Połączenie z bazą danych nawiązane.")
        except mysql.connector.Error as err:
            logger.error(f"Coś poszło nie tak: {err}")

    def show_databases(self):
        if self.cursor:
            self.cursor.execute("SHOW DATABASES")
            databases = self.cursor.fetchall()
            logger.info("Dostępne bazy danych:")
            for db in databases:
                logger.info(db[0])
        else:
            logger.warning("Nie nawiązano połączenia z bazą danych.")

    def show_tables(self):
        if self.cursor:
            self.cursor.execute("SHOW TABLES")
            tables = self.cursor.fetchall()
            logger.info("Dostępne tabele:")
            for tb in tables:
                logger.info(tb[0])
        else:
            logger.warning("Nie nawiązano połączenia z bazą danych.")

    def create_database(self, name_db):
        try:
            self.cursor = self.connection.cursor()
            self.cursor.execute(f"CREATE DATABASE `{name_db}`")
            logger.info(f"Baza danych '{name_db}' została utworzona.")
        except mysql.connector.Error as err:
            logger.error(f"Nie udało się utworzyć bazy danych: {err}")
            self.cursor.close()

    def create_table(self, name_tb):
        try:
            self.cursor = self.connection.cursor()
            self.cursor.execute(
                f"""CREATE TABLE `{name_tb}` (
                    date VARCHAR(255),
                    temperature FLOAT,
                    perceived_temp FLOAT,
                    humidity FLOAT,
                    pressure FLOAT
                )
                """
            )
            logger.info(f"Tabela '{name_tb}' została utworzona.")
        except mysql.connector.Error as err:
            logger.error(f"Nie udało się utworzyć tabeli: {err}")
            self.cursor.close()

    def get_tables(self):
        tables = []
        if self.cursor:
            try:
                self.cursor.execute("SHOW TABLES")
                tables = [table[0] for table in self.cursor.fetchall()]
                logger.info("Dostępne tabele: %s", tables)
            except mysql.connector.Error as err:
                logger.error(f"Nie udało się pobrać tabel: {err}")
        else:
            logger.warning("Nie nawiązano połączenia z bazą danych.")

        return tables

    def delate_table(self, table):
        try:
            self.cursor.execute(f"DROP TABLE `{table}`")
            logger.info(f"Tabela '{table}' została usunięta.")
        except mysql.connector.Error as err:
            logger.error(f"Nie udało się usunąć tabeli '{table}': {err}")

    def delete_all_records(self, table_name):
        try:
            if self.cursor:
                self.cursor.execute(f"DELETE FROM `{table_name}`")
                self.connection.commit()
                logger.info(
                    f"Wszystkie rekordy z tabeli '{table_name}' zostały usunięte."
                )
            else:
                logger.warning("Nie nawiązano połączenia z bazą danych.")
        except mysql.connector.Error as err:
            logger.error(
                f"Nie udało się usunąć rekordów z tabeli '{table_name}': {err}"
            )

    def insert_record(
        self, table_name, date, temperature, perceived_temp, humidity, pressure
    ):
        try:
            if self.cursor:
                self.cursor.execute(
                    f"""INSERT INTO `{table_name}` (date, temperature, perceived_temp, humidity, pressure) 
                    VALUES (%s, %s, %s, %s, %s)""",
                    (date, temperature, perceived_temp, humidity, pressure),
                )
                self.connection.commit()
                logger.info("Rekord został dodany do tabeli '%s'.", table_name)
            else:
                logger.warning("Nie nawiązano połączenia z bazą danych.")
        except mysql.connector.Error as err:
            logger.error(f"Nie udało się dodać rekordu do tabeli '{table_name}': {err}")

    def fetch_records(self, table_name):
        records = []
        try:
            if self.cursor:
                self.cursor.execute(f"SELECT * FROM `{table_name}`")
                records = self.cursor.fetchall()
                logger.info(f"Pobrano rekordy z tabeli '{table_name}': {records}")
            else:
                logger.warning("Nie nawiązano połączenia z bazą danych.")
        except mysql.connector.Error as err:
            logger.error(
                f"Nie udało się pobrać rekordów z tabeli '{table_name}': {err}"
            )

        return records

    def close(self):
        if self.cursor:
            self.cursor.close()
            logger.info("Kursor zamknięty.")
        if self.connection:
            self.connection.close()
            logger.info("Połączenie z bazą danych zamknięte.")


# if __name__ == "__main__":
#     db = Database()
#     records = db.fetch_records("zory")
#     print(records)
#     db.close()
