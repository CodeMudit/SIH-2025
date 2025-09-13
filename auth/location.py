# load_states.py
import json
import requests
from pathlib import Path

def load_states_districts() -> dict:
    local = Path("states-and-districts.json")
    if local.exists():
        with local.open("r", encoding="utf-8") as f:
            return json.load(f)
    url = "https://raw.githubusercontent.com/sab99r/Indian-States-And-Districts/master/states-and-districts.json"
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.json()

states_and_districts = load_states_districts()

from enum import Enum

# Dynamically create Enum for States
StateEnum = Enum(
    "StateEnum",
    {state.replace(" ", "_"): state for state in states_and_districts.keys()},
    type=str
)
