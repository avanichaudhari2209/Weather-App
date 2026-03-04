import customtkinter as ctk
from PIL import Image, ImageTk, ImageDraw
import tkinter as tk
import threading
import os

from weather import get_weather, get_forecast, get_location_by_ip, wind_direction
from config import APP_WIDTH, APP_HEIGHT

APP_TITLE = "Aether — Weather"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

C = {
    "bg":         "#080c14",
    "surface":    "#0b1120",
    "card":       "#0e1628",
    "card2":      "#111d32",
    "border":     "#162035",
    "border_hi":  "#1c3050",
    "accent":     "#0ea5e9",
    "accent2":    "#0284c7",
    "accent_dim": "#0c3d5e",
    "red":        "#f43f5e",
    "text":       "#e2eaf6",
    "text_sec":   "#4e6a8a",
    "text_dim":   "#243348",
    "white":      "#ffffff",
}

F = {
    "brand":      ("Segoe UI Variable Display", 22, "bold"),
    "brand_tag":  ("Segoe UI Variable Small",   10),
    "temp":       ("Segoe UI Variable Display", 62, "bold"),
    "city":       ("Segoe UI Variable Display", 17, "bold"),
    "desc":       ("Segoe UI Variable Text",    12),
    "feels":      ("Segoe UI Variable Small",   10),
    "stat_val":   ("Segoe UI Variable Text",    13, "bold"),
    "stat_lbl":   ("Segoe UI Variable Small",    8, "bold"),
    "hour_time":  ("Segoe UI Variable Small",    9),
    "hour_tmp":   ("Segoe UI Variable Text",    12, "bold"),
    "hour_spd":   ("Segoe UI Variable Small",    8),
    "day_name":   ("Segoe UI Variable Text",    11, "bold"),
    "day_date":   ("Segoe UI Variable Small",    9),
    "day_hi":     ("Segoe UI Variable Text",    12, "bold"),
    "day_lo":     ("Segoe UI Variable Small",   10),
    "sec":        ("Segoe UI Variable Small",    8, "bold"),
    "search":     ("Segoe UI Variable Text",    12),
    "xs":         ("Segoe UI Variable Small",    9),
}

ICON_MAP = {
    "clear":        "assets/icons/clear.png",
    "clouds":       "assets/icons/cloud.png",
    "rain":         "assets/icons/rain.png",
    "drizzle":      "assets/icons/rain.png",
    "snow":         "assets/icons/snow.png",
    "thunderstorm": "assets/icons/thunder.png",
    "mist":         "assets/icons/mist.png",
    "haze":         "assets/icons/mist.png",
    "fog":          "assets/icons/mist.png",
    "smoke":        "assets/icons/mist.png",
}
_cache: dict = {}

def get_img(condition: str, size=(48, 48)):
    key = f"{condition.lower()}_{size}"
    if key in _cache:
        return _cache[key]
    path = ICON_MAP.get(condition.lower(), "assets/icons/cloud.png")
    if os.path.exists(path):
        img = Image.open(path).convert("RGBA").resize(size, Image.LANCZOS)
        r = ctk.CTkImage(light_image=img, dark_image=img, size=size)
        _cache[key] = r
        return r
    return None

def c_to_f(c): return round(c * 9/5 + 32)
def fmt(c, unit): return f"{c}°" if unit == "C" else f"{c_to_f(c)}°"

def make_bg(w, h):
    img = Image.new("RGB", (w, h), C["bg"])
    d = ImageDraw.Draw(img)
    for r in range(500, 0, -3):
        t = 1 - r / 500
        a = int(20 * t * t)
        d.ellipse([-r + 200, -r + 220, r + 200, r + 220],
                  fill=(0, int(a * 0.42), int(a)))
    for r in range(180, 0, -3):
        t = 1 - r / 180
        a = int(12 * t * t)
        d.ellipse([w-r-30, h-r-30, w+r-30, h+r-30],
                  fill=(0, int(a * 0.5), int(a * 0.85)))
    return img


NAV_H    = 60
PAD      = 10
LEFT_W   = 308
CONTENT_Y = NAV_H + PAD
CONTENT_H = APP_HEIGHT - CONTENT_Y - PAD
RIGHT_X  = PAD + LEFT_W + PAD
RIGHT_W  = APP_WIDTH - RIGHT_X - PAD


class AetherApp(ctk.CTk):
    def __init__(self):
        super().__init__(fg_color=C["bg"])
        self.title(APP_TITLE)
        self.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")
        self.resizable(False, False)
        self._unit     = "C"
        self._current  = None
        self._forecast = None
        self._paint_bg()
        self._build()

    def _paint_bg(self):
        self._bg_photo = ImageTk.PhotoImage(make_bg(APP_WIDTH, APP_HEIGHT))
        cv = tk.Canvas(self, width=APP_WIDTH, height=APP_HEIGHT,
                       bd=0, highlightthickness=0)
        cv.place(x=0, y=0)
        cv.create_image(0, 0, anchor="nw", image=self._bg_photo)

    def _build(self):
        self._build_nav()
        self._build_left()
        self._build_right()

    def _build_nav(self):
        nav = ctk.CTkFrame(self, fg_color=C["surface"], height=NAV_H,
                           width=APP_WIDTH, corner_radius=0, border_width=0)
        nav.place(x=0, y=0)
        nav.pack_propagate(False)

        BRAND_W = 210
        brand = ctk.CTkFrame(nav, fg_color="transparent",
                             width=BRAND_W, height=NAV_H)
        brand.place(x=14, y=0)
        brand.pack_propagate(False)

        ctk.CTkLabel(brand, text="✦",
                     font=("Segoe UI Variable Display", 22, "bold"),
                     text_color=C["accent"]).place(x=0, rely=0.5, anchor="w")
        ctk.CTkLabel(brand, text="AETHER",
                     font=F["brand"],
                     text_color=C["text"]).place(x=30, rely=0.5, anchor="w")
        ctk.CTkLabel(brand, text="WEATHER",
                     font=F["brand_tag"],
                     text_color=C["text_dim"]).place(x=146, rely=0.5, anchor="w")

        TOGGLE_W = 104
        TOGGLE_X = APP_WIDTH - TOGGLE_W - 12
        unit_box = ctk.CTkFrame(self, fg_color=C["card"], width=TOGGLE_W, height=34,
                                corner_radius=17, border_width=1,
                                border_color=C["border"])
        unit_box.place(x=TOGGLE_X, y=(NAV_H - 34) // 2)
        unit_box.pack_propagate(False)

        self._uc = ctk.CTkButton(unit_box, text="°C", width=46, height=26,
                                  corner_radius=13,
                                  font=("Segoe UI Variable Text", 10, "bold"),
                                  fg_color=C["accent"], hover_color=C["accent2"],
                                  text_color=C["white"],
                                  command=lambda: self._set_unit("C"))
        self._uc.place(x=3, y=4)
        self._uf = ctk.CTkButton(unit_box, text="°F", width=46, height=26,
                                  corner_radius=13,
                                  font=("Segoe UI Variable Text", 10, "bold"),
                                  fg_color="transparent", hover_color=C["card2"],
                                  text_color=C["text_sec"],
                                  command=lambda: self._set_unit("F"))
        self._uf.place(x=53, y=4)

        S_X      = BRAND_W + 24
        S_RIGHT  = TOGGLE_X - 10
        S_W      = S_RIGHT - S_X
        S_H      = 38

        sf = ctk.CTkFrame(self, fg_color=C["card"], height=S_H, width=S_W,
                          corner_radius=10, border_width=1, border_color=C["border"])
        sf.place(x=S_X, y=(NAV_H - S_H) // 2)
        sf.pack_propagate(False)

        self._sv = ctk.StringVar()
        self._entry = ctk.CTkEntry(
            sf, textvariable=self._sv,
            placeholder_text="Search any city in the world…",
            placeholder_text_color=C["text_dim"],
            font=F["search"], fg_color="transparent",
            border_width=0, text_color=C["text"], height=S_H,
        )
        self._entry.pack(side="left", fill="both", expand=True, padx=(14, 0))
        self._entry.bind("<Return>", lambda e: self._search())

        self._sbtn = ctk.CTkButton(
            sf, text="SEARCH", width=86, height=29, corner_radius=8,
            font=("Segoe UI Variable Small", 9, "bold"),
            fg_color=C["accent"], hover_color=C["accent2"],
            text_color=C["white"], command=self._search,
        )
        self._sbtn.pack(side="right", padx=(0, 4), pady=4)

        self._gbtn = ctk.CTkButton(
            sf, text="GPS", width=58, height=29, corner_radius=8,
            font=("Segoe UI Variable Small", 9, "bold"),
            fg_color=C["card2"], hover_color=C["border_hi"],
            text_color=C["accent"], border_width=1, border_color=C["border"],
            command=self._use_gps,
        )
        self._gbtn.pack(side="right", padx=(0, 3), pady=4)

        tk.Frame(nav, bg=C["border"], height=1).place(x=0, rely=1.0, y=-1, relwidth=1)

    def _build_left(self):
        left = ctk.CTkFrame(self, fg_color=C["card"], width=LEFT_W,
                            height=CONTENT_H, corner_radius=14,
                            border_width=1, border_color=C["border"])
        left.place(x=PAD, y=CONTENT_Y)
        left.pack_propagate(False)

        self._icon_lbl = ctk.CTkLabel(left, text="", image=None)
        self._icon_lbl.pack(pady=(26, 0))

        self._temp_lbl = ctk.CTkLabel(left, text="—°", font=F["temp"],
                                       text_color=C["text"])
        self._temp_lbl.pack(pady=(0, 0))

        self._city_lbl = ctk.CTkLabel(left, text="———————", font=F["city"],
                                       text_color=C["text"], wraplength=280)
        self._city_lbl.pack(pady=(8, 0))

        self._desc_lbl = ctk.CTkLabel(left, text="", font=F["desc"],
                                       text_color=C["accent"])
        self._desc_lbl.pack(pady=(4, 0))

        self._feels_lbl = ctk.CTkLabel(left, text="", font=F["feels"],
                                        text_color=C["text_sec"])
        self._feels_lbl.pack(pady=(2, 0))

        self._status_lbl = ctk.CTkLabel(left, text="", font=F["xs"],
                                         text_color=C["text_dim"])
        self._status_lbl.pack(pady=(4, 0))

        tk.Frame(left, bg=C["border"], height=1).pack(fill="x", padx=18, pady=16)

        grid = ctk.CTkFrame(left, fg_color="transparent")
        grid.pack(padx=12, fill="x")

        self._stats: dict = {}
        items = [
            ("HUMIDITY",   "humidity"),
            ("WIND",       "wind"),
            ("VISIBILITY", "visibility"),
            ("PRESSURE",   "pressure"),
        ]
        for i, (label, key) in enumerate(items):
            r, c = divmod(i, 2)
            cell = ctk.CTkFrame(grid, fg_color=C["surface"], corner_radius=10,
                                border_width=1, border_color=C["border"],
                                width=128, height=60)
            cell.grid(row=r, column=c, padx=4, pady=4, sticky="nsew")
            cell.pack_propagate(False)
            grid.columnconfigure(c, weight=1)
            ctk.CTkLabel(cell, text=label, font=F["stat_lbl"],
                         text_color=C["text_dim"]).pack(anchor="w", padx=10, pady=(8, 0))
            v = ctk.CTkLabel(cell, text="—", font=F["stat_val"],
                             text_color=C["text"])
            v.pack(anchor="w", padx=10, pady=(2, 6))
            self._stats[key] = v

    def _build_right(self):
        right = ctk.CTkFrame(self, fg_color="transparent",
                             width=RIGHT_W, height=CONTENT_H)
        right.place(x=RIGHT_X, y=CONTENT_Y)
        right.pack_propagate(False)

        hdr_h = ctk.CTkFrame(right, fg_color="transparent")
        hdr_h.pack(fill="x", pady=(2, 6))
        ctk.CTkLabel(hdr_h, text="HOURLY", font=F["sec"],
                     text_color=C["accent"]).pack(side="left")
        ctk.CTkLabel(hdr_h, text="  ·  NEXT 24 H", font=F["sec"],
                     text_color=C["text_dim"]).pack(side="left")

        hourly_card = ctk.CTkFrame(right, fg_color=C["surface"], corner_radius=12,
                                    border_width=1, border_color=C["border"],
                                    height=152)
        hourly_card.pack(fill="x")
        hourly_card.pack_propagate(False)

        self._hourly_frame = ctk.CTkFrame(hourly_card, fg_color="transparent")
        self._hourly_frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Frame(right, bg=C["border"], height=1).pack(fill="x", pady=13)

        hdr_d = ctk.CTkFrame(right, fg_color="transparent")
        hdr_d.pack(fill="x", pady=(0, 6))
        ctk.CTkLabel(hdr_d, text="5-DAY", font=F["sec"],
                     text_color=C["accent"]).pack(side="left")
        ctk.CTkLabel(hdr_d, text="  FORECAST", font=F["sec"],
                     text_color=C["text_dim"]).pack(side="left")

        self._daily_frame = ctk.CTkFrame(right, fg_color="transparent")
        self._daily_frame.pack(fill="both", expand=True)

    def _use_gps(self):
        self._set_loading(True, "Detecting location…")
        def task():
            r = get_location_by_ip()
            self.after(0, lambda: self._on_gps(r))
        threading.Thread(target=task, daemon=True).start()

    def _on_gps(self, result):
        if result:
            _, lat, lon = result
            self._load(lat=lat, lon=lon)
        else:
            self._set_loading(False)
            self._status_lbl.configure(text="Could not detect location",
                                        text_color=C["red"])

    def _search(self):
        city = self._sv.get().strip()
        if not city:
            self._status_lbl.configure(text="Enter a city name",
                                        text_color=C["red"])
            return
        self._load(city=city)

    def _load(self, city=None, lat=None, lon=None):
        self._set_loading(True, "Fetching data…")
        def task():
            current  = get_weather(city=city, lat=lat, lon=lon)
            forecast = get_forecast(current["lat"], current["lon"]) if current else None
            self.after(0, lambda: self._on_data(current, forecast))
        threading.Thread(target=task, daemon=True).start()

    def _on_data(self, current, forecast):
        self._set_loading(False)
        if not current:
            self._status_lbl.configure(text="City not found or API error",
                                        text_color=C["red"])
            return
        self._current  = current
        self._forecast = forecast
        self._render_current(current)
        if forecast:
            self._render_hourly(forecast["hourly"])
            self._render_daily(forecast["daily"])

    def _render_current(self, d):
        u = self._unit
        icon = get_img(d["condition"], size=(88, 88))
        if icon:
            self._icon_lbl.configure(image=icon, text="")
        else:
            self._icon_lbl.configure(image=None, text="🌤",
                                      font=("Segoe UI", 54))
        self._temp_lbl.configure(text=fmt(d["temp"], u))
        self._city_lbl.configure(text=f"{d['city']},  {d['country']}")
        self._desc_lbl.configure(text=d["description"])
        self._feels_lbl.configure(text=f"Feels like  {fmt(d['feels_like'], u)}")
        self._status_lbl.configure(text="Updated just now",
                                    text_color=C["text_dim"])
        kph  = d["wind_speed"]
        wdir = wind_direction(d["wind_deg"])
        spd  = (f"{kph} km/h {wdir}" if u == "C"
                else f"{round(kph*0.621,1)} mph {wdir}")
        self._stats["humidity"].configure(text=f"{d['humidity']}%")
        self._stats["wind"].configure(text=spd)
        self._stats["visibility"].configure(text=f"{d['visibility']} km")
        self._stats["pressure"].configure(text=f"{d['pressure']} hPa")

    def _render_hourly(self, slots):
        for w in self._hourly_frame.winfo_children():
            w.destroy()
        u = self._unit
        for slot in slots:
            t = slot["dt_txt"].split()[1][:5]
            card = ctk.CTkFrame(self._hourly_frame, fg_color=C["card"],
                                corner_radius=10, border_width=1,
                                border_color=C["border"], width=84, height=126)
            card.pack(side="left", padx=4)
            card.pack_propagate(False)
            ctk.CTkLabel(card, text=t, font=F["hour_time"],
                         text_color=C["text_sec"]).pack(pady=(10, 2))
            icon = get_img(slot["condition"], size=(30, 30))
            if icon:
                ctk.CTkLabel(card, image=icon, text="").pack(pady=2)
            else:
                ctk.CTkLabel(card, text="🌤", font=("Segoe UI", 16)).pack(pady=2)
            ctk.CTkLabel(card, text=fmt(slot["temp"], u),
                         font=F["hour_tmp"], text_color=C["text"]).pack(pady=(2, 0))
            spd = (slot["wind_speed"] if u == "C"
                   else round(slot["wind_speed"] * 0.621, 1))
            sfx = "k" if u == "C" else "m"
            ctk.CTkLabel(card, text=f"↗ {spd}{sfx}", font=F["hour_spd"],
                         text_color=C["text_dim"]).pack(pady=(1, 8))

    def _render_daily(self, days):
        for w in self._daily_frame.winfo_children():
            w.destroy()
        u = self._unit
        for i, day in enumerate(days):
            row = ctk.CTkFrame(self._daily_frame, fg_color=C["card"],
                               corner_radius=10, border_width=1,
                               border_color=C["border"], height=52)
            row.pack(fill="x", pady=3)
            row.pack_propagate(False)
            if i == 0:
                tk.Frame(row, bg=C["accent"], width=3).pack(side="left", fill="y")
            ctk.CTkLabel(row, text=day["day"], font=F["day_name"],
                         text_color=C["text"], width=44).pack(side="left", padx=(12, 0))
            ctk.CTkLabel(row, text=day["date"], font=F["day_date"],
                         text_color=C["text_sec"], width=58).pack(side="left")
            icon = get_img(day["condition"], size=(24, 24))
            if icon:
                ctk.CTkLabel(row, image=icon, text="").pack(side="left", padx=(6, 4))
            else:
                ctk.CTkLabel(row, text="🌤", font=("Segoe UI", 13)).pack(side="left", padx=(6, 4))
            ctk.CTkLabel(row, text=day["condition"], font=F["xs"],
                         text_color=C["text_sec"]).pack(side="left")
            hi = fmt(day["temp_max"], u)
            lo = fmt(day["temp_min"], u)
            ctk.CTkLabel(row, text=hi, font=F["day_hi"],
                         text_color=C["text"], width=50).pack(side="right", padx=(0, 14))
            ctk.CTkLabel(row, text=lo, font=F["day_lo"],
                         text_color=C["text_dim"], width=42).pack(side="right")

    def _set_unit(self, u):
        self._unit = u
        on, off = (self._uc, self._uf) if u == "C" else (self._uf, self._uc)
        on.configure(fg_color=C["accent"], text_color=C["white"])
        off.configure(fg_color="transparent", text_color=C["text_sec"])
        if self._current:
            self._render_current(self._current)
        if self._forecast:
            self._render_hourly(self._forecast["hourly"])
            self._render_daily(self._forecast["daily"])

    def _set_loading(self, on, msg=""):
        self._status_lbl.configure(
            text=msg,
            text_color=C["accent"] if on else C["text_dim"],
        )
        s = "disabled" if on else "normal"
        self._sbtn.configure(state=s)
        self._gbtn.configure(state=s)


def start_app():
    AetherApp().mainloop()
