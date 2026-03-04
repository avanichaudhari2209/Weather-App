import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY", "")

BASE_URL       = "https://api.openweathermap.org/data/2.5"
GEO_URL        = "https://api.openweathermap.org/geo/1.0"
APP_TITLE = "Aether — Weather"
APP_WIDTH      = 1100
APP_HEIGHT     = 680
CACHE_SECONDS  = 300
