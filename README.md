# Aether — Weather

A sleek, dark-themed desktop weather application built with Python and CustomTkinter. Aether provides real-time weather data, hourly forecasts, and 5-day outlooks with a polished, modern UI.

![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square)
![CustomTkinter](https://img.shields.io/badge/UI-CustomTkinter-informational?style=flat-square)
![OpenWeatherMap](https://img.shields.io/badge/API-OpenWeatherMap-orange?style=flat-square)

---

## Features

- **Auto-detect location** via IP geolocation
- **Search any city** worldwide
- **Current conditions** — temperature, feels-like, humidity, wind, visibility, pressure
- **Hourly forecast** — next 24 hours in 3-hour steps
- **5-day forecast** — daily high/low with weather condition
- **°C / °F toggle** — instant unit switching
- **Response caching** — avoids redundant API calls (5-minute TTL)
- **Custom weather icons** — mapped by condition type

---

##  Project Structure

```
aether-weather/
├── main.py            # Entry point — launches the app
├── ui.py              # Full UI layer (CustomTkinter window & widgets)
├── weather.py         # Weather data fetching, parsing, and caching
├── config.py          # App settings and API configuration
├── requirements.txt   # Python dependencies
└── assets/
    └── icons/
        ├── clear.png
        ├── cloud.png
        ├── rain.png
        ├── snow.png
        ├── thunder.png
        └── mist.png
```

---

##  Getting Started

### Prerequisites

- Python 3.8 or higher
- An [OpenWeatherMap](https://openweathermap.org/api) API key (free tier works)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/aether-weather.git
   cd aether-weather
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure your API key**

   Create a `.env` file in the project root:
   ```env
   OPENWEATHER_API_KEY=your_api_key_here
   ```

   > A fallback key is included in `config.py` for testing, but it may be rate-limited. It's recommended to use your own key.

4. **Add weather icons**

   Place the following PNG icons in `assets/icons/`:
   `clear.png`, `cloud.png`, `rain.png`, `snow.png`, `thunder.png`, `mist.png`

5. **Run the app**
   ```bash
   python main.py
   ```

---

## Configuration

All settings are managed in `config.py`:

| Variable | Default | Description |
|---|---|---|
| `API_KEY` | *(from .env)* | OpenWeatherMap API key |
| `BASE_URL` | `https://api.openweathermap.org/data/2.5` | Weather API base URL |
| `GEO_URL` | `https://api.openweathermap.org/geo/1.0` | Geocoding API base URL |
| `APP_WIDTH` | `1100` | Window width in pixels |
| `APP_HEIGHT` | `680` | Window height in pixels |
| `CACHE_SECONDS` | `300` | Cache TTL in seconds (5 minutes) |

---

## Dependencies

| Package | Purpose |
|---|---|
| `requests` | HTTP calls to OpenWeatherMap & IP geolocation APIs |
| `pillow` | Image processing for icons and background rendering |
| `customtkinter` | Modern themed Tkinter UI widgets |
| `python-dotenv` | Loading API keys from `.env` file |

---

## How It Works

1. **Location** — On launch, clicking the GPS button calls `ipapi.co` to resolve approximate coordinates from the user's IP address.
2. **Search** — Typing a city name triggers the OpenWeatherMap Geocoding API to resolve coordinates, then fetches weather for those coordinates.
3. **Weather data** — `weather.py` fetches current conditions and a 3-hour interval 5-day forecast from the OpenWeatherMap API. Results are cached in memory.
4. **UI rendering** — `ui.py` renders all panels: current stats, hourly cards, and daily forecast rows. Unit toggling (°C/°F) re-renders all displayed values instantly without a new API call.

---

## License

This project is open-source. Feel free to use, modify, and distribute it.
