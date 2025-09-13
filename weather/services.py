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