import json
import requests

# Option A: load from local file
with open("states-and-districts.json", "r", encoding="utf-8") as f:
    states_and_districts = json.load(f)

# Option B: fetch from GitHub raw
url = "https://raw.githubusercontent.com/sab99r/Indian-States-And-Districts/master/states-and-districts.json"
resp = requests.get(url)
resp.raise_for_status()
states_and_districts = resp.json()
