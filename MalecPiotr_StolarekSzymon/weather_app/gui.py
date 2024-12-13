import tkinter as tk
import tkinter.font as tkFont
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np
from controller import Controller
from PIL import Image, ImageTk
from datetime import datetime, timedelta


class Gui:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather app")
        self.root.geometry("1920x1080")
        self.root.config(bg="#e6f7ff")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.controller = Controller()
        self.city_var = tk.StringVar()
        self.selected_day = tk.StringVar()
        self.create_widgets()
        self.h_scale = tk.StringVar()
        self.p_scale = tk.StringVar()
        self.temp_min = tk.StringVar()
        self.temp_max = tk.StringVar()

    def create_widgets(self):
        image = Image.open("logo.png")
        resized_image = image.resize((300, 300))
        logo_image = ImageTk.PhotoImage(resized_image)
        logo_label = tk.Label(self.root, image=logo_image, bg="#e6f7ff")
        logo_label.image = logo_image
        logo_label.pack(pady=20)

        city_label = tk.Label(
            self.root,
            text="Please enter the city name:",
            bg="#e6f7ff",
            font=tkFont.Font(size=14),
        )
        city_label.pack(pady=5)

        city_entry = tk.Entry(self.root, textvariable=self.city_var, width=40)
        city_entry.pack(pady=50)

        self.days = [
            (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(5)
        ]

        self.selected_day.set(self.days[0])

        day_label = tk.Label(
            self.root,
            text="Select a day:",
            bg="#e6f7ff",
            font=tkFont.Font(size=14),
        )
        day_label.pack(pady=5)

        day_menu = tk.OptionMenu(self.root, self.selected_day, *self.days)
        day_menu.pack(pady=5)

        check_button = tk.Button(
            self.root, text="Check", command=self.open_second_window
        )
        check_button.config(height=6, width=40)
        check_button.pack(pady=20)

        self.second_window = tk.Toplevel(self.root)
        self.second_window.title("Weather app")
        self.second_window.geometry("1920x1080")
        self.second_window.config(bg="#e6f7ff")
        self.second_window.withdraw()
        self.second_window.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_weather_plot(self, city_name):
        days = []
        temperatures = []
        feels_like = []
        humidity = []
        pressure = []
        data = self.controller.process(city_name)
        selected_day = self.selected_day.get()
        filtered_data = [entry for entry in data if entry[0][:10] == selected_day]

        for num in range(len(filtered_data)):
            days.append(filtered_data[num][0][11:20])
            temperatures.append(filtered_data[num][1])
            feels_like.append(filtered_data[num][2])
            humidity.append(filtered_data[num][3])
            pressure.append(filtered_data[num][4])

        fig, ax1 = plt.subplots(figsize=(10, 6))

        ax1.bar(
            np.arange(len(days)) - 0.1,
            humidity,
            width=0.2,
            color="lightblue",
            label="Humidity (%)",
        )

        ax3 = ax1.twinx()
        ax3.bar(
            np.arange(len(days)) + 0.1,
            pressure,
            width=0.2,
            color="lightgray",
            label="Pressure (hPa)",
        )

        ax2 = ax1.twinx()
        ax2.plot(days, temperatures, marker="o", color="red", label="Temperature")
        ax2.plot(days, feels_like, marker="o", color="blue", label="Feels Like Temp.")

        ax1.set_xlabel("Days")
        ax1.set_ylabel("Humidity (%)", color="black", labelpad=2)
        ax1.tick_params(axis="y")
        ax2.set_ylabel("Temperature (°C)", color="black", labelpad=15)
        ax2.yaxis.set_label_position("right")
        ax3.spines["left"].set_position(("outward", 40))
        ax3.yaxis.tick_left()
        ax3.set_ylabel("Pressure (hPa)", color="black", labelpad=2)
        ax3.yaxis.set_label_position("left")

        try:
            p_scale_max = float(self.p_scale.get())
            ax3.set_ylim(0, p_scale_max)
        except ValueError:
            pass

        try:
            h_scale_max = float(self.h_scale.get())
            ax1.set_ylim(0, h_scale_max)
        except ValueError:
            pass

        try:
            t_max = float(self.temp_max.get())
            t_min = float(self.temp_min.get())
            ax2.set_ylim(ymin=t_min, ymax=t_max)
        except ValueError:
            pass

        fig.suptitle(f"{city_name.capitalize()} - {selected_day}")
        ax1.legend(loc="upper left")
        ax2.legend(loc="upper right")
        ax3.legend(loc="upper center")

        avg_temp = np.mean(temperatures)
        avg_feels_like = np.mean(feels_like)
        avg_humidity = np.mean(humidity)
        avg_pressure = np.mean(pressure)

        fig.text(
            0.5,
            0.00,
            f"Average - Temperature: {round(avg_temp)} °C, Feels Like: {round(avg_feels_like)} °C, Humidity: {round(avg_humidity)} %, Pressure: {round(avg_pressure)} hPa",
            ha="center",
            fontsize=12,
            va="bottom",
        )

        return fig

    def on_closing(self):
        self.controller.close()
        self.root.quit()
        self.root.destroy()
        self.second_window.quit()
        self.second_window.destroy()

    def open_second_window(self):

        for widget in self.second_window.winfo_children():
            widget.destroy()

        city_name = self.city_var.get().lower()
        weather = self.create_weather_plot(city_name)
        canvas = FigureCanvasTkAgg(weather, master=self.second_window)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=20)

        frame_scale = tk.Frame(self.second_window)
        frame_scale.pack(pady=10)
        frame_scale.config(bg="#e6f7ff")

        data = self.controller.fetch_records(city_name)
        self.days = sorted(list({entry[0].split()[0] for entry in data}))

        self.selected_day.set(self.days[0])

        day_label = tk.Label(
            frame_scale,
            text="Select a day:",
            bg="#e6f7ff",
            font=tkFont.Font(size=14),
        )
        day_label.pack(pady=10, padx=10, side=tk.LEFT)

        day_menu = tk.OptionMenu(frame_scale, self.selected_day, *self.days)
        day_menu.pack(pady=10, padx=10, side=tk.LEFT)

        p_frame = tk.Frame(frame_scale, bg="#e6f7ff")
        p_frame.pack(side=tk.LEFT, pady=10, padx=10)

        ptext_label = tk.Label(
            p_frame, text="Scale for preasure:", bg="#e6f7ff", font=tkFont.Font(size=14)
        )
        ptext_label.pack(pady=10, padx=10)
        p_max_label = tk.Label(
            p_frame,
            fg="#FF0000",
            text="Max scale:",
            bg="#e6f7ff",
            font=tkFont.Font(size=14),
        )
        p_max_label.pack(pady=10, padx=10)
        p_entry = tk.Entry(p_frame, textvariable=self.p_scale, width=40)
        p_entry.pack(pady=10, padx=10)

        h_frame = tk.Frame(frame_scale, bg="#e6f7ff")
        h_frame.pack(side=tk.LEFT, pady=10, padx=10)

        htext_label = tk.Label(
            h_frame,
            text="Scale for humidity (max):",
            bg="#e6f7ff",
            font=tkFont.Font(size=14),
        )
        htext_label.pack(pady=10, padx=10)
        h_max_label = tk.Label(
            h_frame,
            fg="#FF0000",
            text="Max scale:",
            bg="#e6f7ff",
            font=tkFont.Font(size=14),
        )
        h_max_label.pack(pady=10, padx=10)
        h_entry = tk.Entry(h_frame, textvariable=self.h_scale, width=40)
        h_entry.pack(pady=10, padx=10)

        temperature_frame = tk.Frame(frame_scale, bg="#e6f7ff")
        temperature_frame.pack(side=tk.RIGHT, pady=10, padx=10)

        temp_label = tk.Label(
            temperature_frame,
            text="Scale for temperature:",
            bg="#e6f7ff",
            font=tkFont.Font(size=14),
        )
        temp_label.pack(pady=5, padx=10)

        temp_max_frame = tk.Frame(temperature_frame, bg="#e6f7ff")
        temp_max_frame.pack(side=tk.LEFT, pady=10, padx=10)
        temp_max_label = tk.Label(
            temp_max_frame,
            fg="#FF0000",
            text="Max scale:",
            bg="#e6f7ff",
            font=tkFont.Font(size=14),
        )
        temp_max_label.pack(pady=10, padx=10)

        t_max_entry = tk.Entry(temp_max_frame, textvariable=self.temp_max, width=40)
        t_max_entry.pack(pady=10, padx=10)

        temp_min_frame = tk.Frame(temperature_frame, bg="#e6f7ff")
        temp_min_frame.pack(side=tk.LEFT, pady=10, padx=10)
        temp_min_label = tk.Label(
            temp_min_frame,
            fg="#0000FF",
            text="Min scale:",
            bg="#e6f7ff",
            font=tkFont.Font(size=14),
        )
        temp_min_label.pack(pady=10, padx=10)
        t_min_entry = tk.Entry(temp_min_frame, textvariable=self.temp_min, width=40)
        t_min_entry.pack(pady=10, padx=10)

        frame_button = tk.Frame(self.second_window)
        frame_button.pack(pady=10)
        frame_button.config(bg="#e6f7ff")

        change_button = tk.Button(
            frame_button, text="Change scale", command=self.open_second_window
        )
        change_button.pack(side=tk.LEFT, pady=10, padx=10)
        change_button.config(height=6, width=40)

        back_button = tk.Button(frame_button, text="Back", command=self.go_back)
        back_button.pack(side=tk.LEFT, pady=10, padx=10)
        back_button.config(height=6, width=40)

        self.root.withdraw()
        self.second_window.deiconify()

    def go_back(self):
        self.second_window.withdraw()
        self.root.deiconify()

if __name__ == "__main__":
    root = tk.Tk()
    app = Gui(root)
    root.mainloop()
