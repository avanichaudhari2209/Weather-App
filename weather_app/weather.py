import requests
import time
from config import API_KEY, BASE_URL, GEO_URL, CACHE_SECONDS

_cache: dict = {}

def _cached(key, fetcher):
    entry = _cache.get(key)
    if entry and time.time() - entry["ts"] < CACHE_SECONDS:
        return entry["data"]
    result = fetcher()
    if result:
        _cache[key] = {"ts": time.time(), "data": result}
    return result


def get_location_by_ip():
    try:
        r = requests.get("https://ipapi.co/json/", timeout=6)
        d = r.json()
        return d.get("city", ""), float(d["latitude"]), float(d["longitude"])
    except Exception:
        return None


def get_coords_for_city(city: str):
    try:
        url = f"{GEO_URL}/direct?q={city}&limit=1&appid={API_KEY}"
        r = requests.get(url, timeout=8)
        data = r.json()
        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception:
        pass
    return None


def get_weather(city: str = None, lat: float = None, lon: float = None):
    if lat is not None and lon is not None:
        cache_key = f"current_{lat:.3f}_{lon:.3f}"
        def fetch():
            return _fetch_current_latlon(lat, lon)
    else:
        cache_key = f"current_{city}"
        def fetch():
            return _fetch_current_city(city)

    return _cached(cache_key, fetch)


def _fetch_current_city(city):
    try:
        url = f"{BASE_URL}/weather?q={city}&units=metric&appid={API_KEY}"
        r = requests.get(url, timeout=10)
        return _parse_current(r.json())
    except Exception:
        return None


def _fetch_current_latlon(lat, lon):
    try:
        url = f"{BASE_URL}/weather?lat={lat}&lon={lon}&units=metric&appid={API_KEY}"
        r = requests.get(url, timeout=10)
        return _parse_current(r.json())
    except Exception:
        return None


def _parse_current(data):
    if data.get("cod") != 200:
        return None
    wind = data.get("wind", {})
    return {
        "city":        data["name"],
        "country":     data["sys"].get("country", ""),
        "temp":        round(data["main"]["temp"]),
        "feels_like":  round(data["main"]["feels_like"]),
        "humidity":    data["main"]["humidity"],
        "condition":   data["weather"][0]["main"],
        "description": data["weather"][0]["description"].title(),
        "wind_speed":  round(wind.get("speed", 0) * 3.6, 1),
        "wind_deg":    wind.get("deg", 0),
        "visibility":  round(data.get("visibility", 0) / 1000, 1),
        "pressure":    data["main"].get("pressure", 0),
        "lat":         data["coord"]["lat"],
        "lon":         data["coord"]["lon"],
    }


def get_forecast(lat: float, lon: float):
    cache_key = f"forecast_{lat:.3f}_{lon:.3f}"
    def fetch():
        return _fetch_forecast(lat, lon)
    return _cached(cache_key, fetch)


def _fetch_forecast(lat, lon):
    try:
        url = (
            f"{BASE_URL}/forecast"
            f"?lat={lat}&lon={lon}&units=metric&appid={API_KEY}"
        )
        r = requests.get(url, timeout=10)
        data = r.json()
        if data.get("cod") != "200":
            return None

        items = data["list"]

        hourly = []
        for item in items[:8]:
            hourly.append({
                "dt_txt":    item["dt_txt"],
                "temp":      round(item["main"]["temp"]),
                "condition": item["weather"][0]["main"],
                "wind_speed": round(item["wind"]["speed"] * 3.6, 1),
            })

        from collections import defaultdict
        import datetime

        days: dict = defaultdict(list)
        for item in items:
            date = item["dt_txt"].split()[0]
            days[date].append(item)

        daily = []
        for date, slots in list(days.items())[:5]:
            dt = datetime.datetime.strptime(date, "%Y-%m-%d")
            day_name = dt.strftime("%a")
            temps  = [s["main"]["temp"] for s in slots]
            conds  = [s["weather"][0]["main"] for s in slots]
            condition = max(set(conds), key=conds.count)
            daily.append({
                "day":       day_name,
                "date":      dt.strftime("%d %b"),
                "temp_min":  round(min(temps)),
                "temp_max":  round(max(temps)),
                "condition": condition,
            })

        return {"hourly": hourly, "daily": daily}

    except Exception:
        return None


def wind_direction(deg: int) -> str:
    dirs = ["N","NE","E","SE","S","SW","W","NW"]
    return dirs[round(deg / 45) % 8]
