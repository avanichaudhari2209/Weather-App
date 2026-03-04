# ui.py

import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
from weather import get_weather


APP_WIDTH = 900
APP_HEIGHT = 600


def load_icon(path, size=(90, 90)):
    if os.path.exists(path):
        img = Image.open(path).resize(size)
        return ImageTk.PhotoImage(img)
    return None

def get_icon_path(condition):
    condition = condition.lower()

    if condition == "clouds":
        return "assets/icons/cloud.png"
    elif condition=="clear":
        return "assets/icons/clear.png"
    elif condition == "rain":
        return "assets/icons/rain.png"
    elif condition == "snow":
        return "assets/icons/snow.png"
    elif condition == "thunderstorm":
        return "assets/icons/thunder.png"
    elif condition in ["mist", "haze", "fog", "smoke"]:
        return "assets/icons/mist.png"
    else:
        return "assets/icons/cloud.png"

def start_app():
    app = tk.Tk()
    app.title("Real-Time Weather Forecast")
    app.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")
    app.resizable(False, False)

    # Background
    if os.path.exists("assets/background.png"):
        bg = ImageTk.PhotoImage(
            Image.open("assets/background.png").resize((APP_WIDTH, APP_HEIGHT))
        )
        bg_label = tk.Label(app, image=bg)
        bg_label.place(relwidth=1, relheight=1)
        bg_label.image = bg
    else:
        app.configure(bg="#87CEEB")

    # Main Card
    card = tk.Frame(app, bg="white", bd=0)
    card.place(relx=0.5, rely=0.52, anchor="center", width=480, height=420)

    # Title
    tk.Label(
        card,
        text="Weather Forecast",
        font=("Segoe UI", 22, "bold"),
        bg="white"
    ).pack(pady=(20, 10))

    # City Input
    city_entry = ttk.Entry(card, font=("Segoe UI", 12))
    city_entry.pack(padx=30, pady=10, fill="x")
    city_entry.focus()

    # Weather Icon Holder (fixed size)
    icon_frame = tk.Frame(card, bg="white", width=100, height=100)
    icon_frame.pack(pady=10)
    icon_frame.pack_propagate(False)

    icon_label = tk.Label(icon_frame, bg="white")
    icon_label.place(relx=0.5, rely=0.5, anchor="center")

    # Weather Info
    result_label = tk.Label(
        card,
        font=("Segoe UI", 12),
        bg="white",
        justify="center"
    )
    result_label.pack(pady=10)

    # Buttons
    btn_frame = tk.Frame(card, bg="white")
    btn_frame.pack(pady=10)

    def show_weather():
        city = city_entry.get().strip()
        if not city:
            messagebox.showwarning("Input Error", "Please enter a city name")
            return

        data = get_weather(city)
        if not data:
            messagebox.showerror("Error", "City not found or API error")
            return

        icon = load_icon(get_icon_path(data["condition"]))

        if icon:
            icon_label.config(image=icon)
            icon_label.image = icon
        else:
            icon_label.config(image="", text="")

        result_label.config(
            text=(
                f"{data['city']}\n"
                f"Temperature: {data['temp']} °C\n"
                f"Humidity: {data['humidity']}%\n"
                f"Condition: {data['description']}"
            )
        )

    ttk.Button(
        btn_frame,
        text="Get Weather",
        command=show_weather,
        width=18
    ).grid(row=0, column=0, padx=10)

    def use_location():
        messagebox.showinfo(
            "Location",
            "Location-based weather can be added using a GPS API"
        )

    ttk.Button(
        btn_frame,
        text="Use My Location",
        command=use_location,
        width=18
    ).grid(row=0, column=1, padx=10)

    city_entry.bind("<Return>", lambda e: show_weather())

    app.mainloop()