import requests

def get_location_from_coords(lat: float, lon: float) -> dict:
    url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
    try:
        resp = requests.get(url, headers={"User-Agent": "farmer-app"})
        resp.raise_for_status()
        data = resp.json()
        address = data.get("address", {})
        state = address.get("state", "Unknown")
        district = (
            address.get("county") or 
            address.get("state_district") or 
            "Unknown"
        )
        return {"state": state, "district": district}
    except Exception as e:
        print("Error fetching location:", str(e))
        return {"state": "Unknown", "district": "Unknown"}
