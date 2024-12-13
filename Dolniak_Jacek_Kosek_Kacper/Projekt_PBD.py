import tkinter as tk
from tkinter import Canvas
import requests
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import urllib3
import pymysql
from collections import deque
import pandas as pd
import pdfkit
import os
from sqlalchemy import create_engine

# Disable InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class ScadaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SCADA App")
        self.root.geometry("1920x1080")

        # Database connection
        self.db_connection = pymysql.connect(
            host="localhost",
            user="root",
            password="Razer1035.,",
            database="scada_db"
        )

        # Create SQLAlchemy engine
        self.engine = create_engine("mysql+pymysql://root:Razer1035.,@localhost/scada_db")

        # Frame for analog meter
        self.meter_frame = tk.Frame(self.root, width=400, height=300)
        self.meter_frame.grid(row=0, column=0, padx=340, pady=10, sticky='n')

        # Create canvas for analog meter (progress bar-like indicator)
        self.canvas = Canvas(self.meter_frame, width=400, height=300, bg='white')
        self.canvas.pack(expand=True)

        # Initial value for power
        self.power_value = 0.0

        # Frame for weather information
        self.weather_frame = tk.Frame(self.root, width=400, height=300)
        self.weather_frame.grid(row=1, column=0, padx=340, pady=10, sticky='n')

        # Labels to display weather data
        self.temperature_label = tk.Label(self.weather_frame, text="Temperatura: N/A", font=("Arial", 16))
        self.temperature_label.pack(anchor='center')
        self.wind_speed_label = tk.Label(self.weather_frame, text="Prędkość wiatru: N/A", font=("Arial", 16))
        self.wind_speed_label.pack(anchor='center')
        self.wind_direction_label = tk.Label(self.weather_frame, text="Kierunek wiatru: N/A", font=("Arial", 16))
        self.wind_direction_label.pack(anchor='center')
        self.humidity_label = tk.Label(self.weather_frame, text="Wilgotność: N/A", font=("Arial", 16))
        self.humidity_label.pack(anchor='center')
        self.precipitation_label = tk.Label(self.weather_frame, text="Opady: N/A", font=("Arial", 16))
        self.precipitation_label.pack(anchor='center')
        self.pressure_label = tk.Label(self.weather_frame, text="Ciśnienie: N/A", font=("Arial", 16))
        self.pressure_label.pack(anchor='center')

        # Create frame for power chart
        self.plot_frame = tk.Frame(self.root, width=400, height=300)
        self.plot_frame.grid(row=2, column=0, padx=340, pady=10, sticky='n')

        # Create matplotlib figure for power chart
        self.figure = Figure(figsize=(10, 4), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title("Moc w ciągu ostatnich 12 godzin")
        self.ax.set_xlabel("Czas")
        self.ax.set_ylabel("Moc (kW)")
        self.ax.set_yticks([2000, 4000, 6000, 8000])  # Set constant y-axis values
        self.ax.set_ylim(0, 8000)  # Fix the y-axis limits to prevent scaling
        self.ax.grid(True)  # Add grid to the chart
        self.power_data = deque(maxlen=480)  # Initialize deque with a maximum length
        self.time_data = deque(maxlen=480)  # Store corresponding time values
        self.chart = FigureCanvasTkAgg(self.figure, master=self.plot_frame)
        self.chart.get_tk_widget().pack(expand=True)

        # Create frame for control buttons
        self.control_frame = tk.Frame(self.root, width=200, height=300)
        self.control_frame.grid(row=0, column=1, rowspan=6, padx=20, pady=10, sticky='n')

        # Button to generate report
        self.report_button = tk.Button(self.control_frame, text="Generowanie Raportu", command=self.generate_report)
        self.report_button.pack(pady=10)

        # Button to clear database
        self.clear_db_button = tk.Button(self.control_frame, text="Reset Bazy Danych", command=self.clear_database)
        self.clear_db_button.pack(pady=10)

        # Button to exit the application
        self.exit_button = tk.Button(self.control_frame, text="Zamknij", command=self.exit_application)
        self.exit_button.pack(pady=10)

        # Start the data update loop
        self.update_data()

    def update_data(self):
        # Fetch data and update charts and UI
        self.get_power_data()
        self.get_weather_data()
        self.update_meter()
        self.update_power_chart()

        # Schedule the next update (every 3 seconds)
        self.root.after(3000, self.update_data)

    def update_power_chart(self):
        self.ax.clear()
        self.ax.set_title("Przebieg Mocy Baterii Fotowoltaicznej")
        self.ax.set_xlabel("Czas")
        self.ax.set_ylabel("Moc (kW)")
        self.ax.set_yticks([2000, 4000, 6000, 8000])  # Set constant y-axis values
        self.ax.set_ylim(0, 8000)  # Fix the y-axis limits to prevent scaling
        self.ax.grid(True)  # Add grid to the chart

        # Plot the filtered data
        if self.power_data:
            self.ax.plot(self.time_data, self.power_data, color='Slateblue', alpha=0.6)
            self.ax.set_xlim([datetime.now() - timedelta(hours=12), datetime.now()])
        self.chart.draw()

    def update_meter(self):
        self.canvas.delete("all")
        percentage = min(100, max(0, (self.power_value / 8000) * 100))
        color = "red" if percentage >= 75 else "yellow" if percentage >= 50 else "green" if percentage >= 25 else "grey"
        self.canvas.create_rectangle(50, 100, 350, 200, fill="lightgrey", outline="black")
        self.canvas.create_rectangle(50, 100, 50 + 3 * percentage, 200, fill=color, outline="black")
        self.canvas.create_text(200, 150, text=f"{int(percentage)}%", font=("Arial", 16))
        self.canvas.create_text(200, 250, text=f"Power: {int(self.power_value)} W", font=("Arial", 16))

    def get_power_data(self):
        try:
            response = requests.get("https://91.233.250.151:5555/dyn/getDashValues.json", verify=False, timeout=5)
            if response.status_code == 200:
                data = response.json()
                power_data = data.get("result", {}).get("0198-xxxxx100", {}).get("6100_40263F00", {}).get("1", [])[0]
                if "val" in power_data:
                    self.power_value = power_data["val"]
                    now = datetime.now()
                    self.power_data.append(self.power_value)
                    self.time_data.append(now)

                    # Insert data into the database
                    with self.db_connection.cursor() as cursor:
                        sql = "INSERT INTO power_data (Czas, Moc) VALUES (%s, %s)"
                        cursor.execute(sql, (now, self.power_value))
                        self.db_connection.commit()
        except Exception as e:
            print(f"Error fetching power data: {e}")

    def get_weather_data(self):
        try:
            url = "https://danepubliczne.imgw.pl/api/data/synop"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                for station_data in data:
                    if station_data['stacja'] == 'Katowice':
                        temperature = station_data.get('temperatura', None)
                        wind_speed = station_data.get('predkosc_wiatru', None)
                        wind_direction = station_data.get('kierunek_wiatru', None)
                        humidity = station_data.get('wilgotnosc_wzgledna', None)
                        precipitation = station_data.get('suma_opadu', None)
                        pressure = station_data.get('cisnienie', None)
                        
                        self.temperature_label.config(text=f"Temperatura: {temperature}°C")
                        self.wind_speed_label.config(text=f"Prędkość wiatru: {wind_speed} km/h")
                        self.wind_direction_label.config(text=f"Kierunek wiatru: {wind_direction}°")
                        self.humidity_label.config(text=f"Wilgotność: {humidity}%")
                        self.precipitation_label.config(text=f"Opady: {precipitation} mm")
                        self.pressure_label.config(text=f"Ciśnienie: {pressure} hPa")

                        # Insert data into the database
                        now = datetime.now()
                        with self.db_connection.cursor() as cursor:
                            sql = """
                                INSERT INTO weather_data (
                                    Czas, temperatura, predkosc_wiatru, kierunek_wiatru,
                                    wilgotnosc, opady, cisnienie
                                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                            """
                            cursor.execute(sql, (now, temperature, wind_speed, wind_direction,
                                                 humidity, precipitation, pressure))
                            self.db_connection.commit()
                        break
        except Exception as e:
            print(f"Error fetching weather data: {e}")


    def generate_report(self):
        try:
            # Get the current date and time for the filename
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            
            # Connect to the database using SQLAlchemy
            df_power = pd.read_sql("SELECT * FROM power_data", self.engine)
            df_weather = pd.read_sql("SELECT * FROM weather_data", self.engine)

            # Generate HTML report
            html_content = df_power.to_html() + "<br><br>" + df_weather.to_html()
            html_filename = f"report_{timestamp}.html"
            with open(html_filename, "w") as html_file:
                html_file.write(html_content)

            # Path to wkhtmltopdf
            path_to_wkhtmltopdf = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
            pdfkit_config = pdfkit.configuration(wkhtmltopdf=path_to_wkhtmltopdf)

            # Convert HTML to PDF
            pdf_filename = f"report_{timestamp}.pdf"
            pdfkit.from_file(html_filename, pdf_filename, configuration=pdfkit_config)

            # Create and save chart as JPG
            jpg_filename = f"report_{timestamp}.jpg"
            plt.figure(figsize=(10, 6))
            plt.plot(df_power['Czas'], df_power['Moc'], label="Moc (kW)", color='blue')
            plt.xlabel('Czas')
            plt.ylabel('Moc (kW)')
            plt.title('Przebieg Mocy')
            plt.grid(True)
            plt.savefig(jpg_filename)
            plt.close()

            print(f"Report generated successfully:\nHTML: {html_filename}\nPDF: {pdf_filename}\nJPG: {jpg_filename}")

        except Exception as e:
            print(f"Error generating report: {e}")


    def clear_database(self):
        try:
            with self.db_connection.cursor() as cursor:
                cursor.execute("DELETE FROM power_data")
                cursor.execute("DELETE FROM weather_data")
                self.db_connection.commit()
            print("Database cleared successfully.")
        except Exception as e:
            print(f"Error clearing database: {e}")

    def exit_application(self):
        self.root.destroy()
        print("Application closed.")

if __name__ == "__main__":
    root = tk.Tk()
    app = ScadaApp(root)
    root.mainloop()
