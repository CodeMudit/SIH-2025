import requests
def fetch_weather(location: str) -> dict:
    url = f"http://wttr.in/{location}?format=j1"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        current = data.get("current_condition", [{}])[0]
        return {
            "location": location,
            "temperature_c": current.get("temp_C"),
            "temperature_f": current.get("temp_F"),
            "description": current.get("weatherDesc", [{}])[0].get("value"),
            "humidity": current.get("humidity"),
            "wind_speed_kph": current.get("windspeedKmph"),
            "feels_like_c": current.get("FeelsLikeC"),
        }
    except requests.RequestException as e:
        return {"error": f"Failed to fetch weather: {str(e)}"}


def fetch_weather_by_coords(lat: float, lon: float) -> dict:
    """
    Fetch current weather and a short forecast using Open-Meteo (no API key required).
    """
    try:
        base = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": [
                "temperature_2m",
                "relative_humidity_2m",
                "wind_speed_10m",
                "weather_code",
            ],
            "hourly": ["temperature_2m"],
            "daily": ["temperature_2m_max", "temperature_2m_min"],
            "timezone": "auto",
        }
        resp = requests.get(base, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        current = data.get("current", {})
        daily = data.get("daily", {})

        def wmo_desc(code: int) -> str:
            mapping = {
                0: "Clear sky",
                1: "Mainly clear",
                2: "Partly cloudy",
                3: "Overcast",
                45: "Fog",
                48: "Depositing rime fog",
                51: "Light drizzle",
                53: "Moderate drizzle",
                55: "Dense drizzle",
                61: "Slight rain",
                63: "Moderate rain",
                65: "Heavy rain",
                71: "Slight snow",
                73: "Moderate snow",
                75: "Heavy snow",
                95: "Thunderstorm",
            }
            return mapping.get(code, "Unknown")

        return {
            "temperature_c": current.get("temperature_2m"),
            "humidity": current.get("relative_humidity_2m"),
            "wind_speed_kmh": current.get("wind_speed_10m"),
            "condition": wmo_desc(current.get("weather_code", -1)),
            "forecast": [
                {
                    "date": d,
                    "temp_max_c": tmax,
                    "temp_min_c": tmin,
                }
                for d, tmax, tmin in zip(
                    daily.get("time", []) or [],
                    daily.get("temperature_2m_max", []) or [],
                    daily.get("temperature_2m_min", []) or [],
                )
            ],
        }
    except requests.RequestException as e:
        return {"error": f"Failed to fetch weather: {str(e)}"}