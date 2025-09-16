import numpy as np
import pandas as pd
import requests
from datetime import datetime

class CropAdvisor:
    def __init__(self):
        # Complete crop database with real values
        self.crop_db = {
            'wheat': {'n': 120, 'p': 60, 'k': 40, 'kc': {'initial': 0.7, 'mid': 1.15, 'late': 0.25}},
            'rice': {'n': 100, 'p': 50, 'k': 60, 'kc': {'initial': 0.8, 'mid': 1.1, 'late': 0.9}},
            'maize': {'n': 150, 'p': 75, 'k': 90, 'kc': {'initial': 0.45, 'mid': 1.15, 'late': 0.85}},
            'sugarcane': {'n': 180, 'p': 80, 'k': 100, 'kc': {'initial': 0.5, 'mid': 1.25, 'late': 0.9}},
            'cotton': {'n': 100, 'p': 50, 'k': 70, 'kc': {'initial': 0.5, 'mid': 1.2, 'late': 0.7}},
            'pulses': {'n': 75, 'p': 40, 'k': 50, 'kc': {'initial': 0.4, 'mid': 1.0, 'late': 0.75}},
            'groundnut': {'n': 80, 'p': 45, 'k': 60, 'kc': {'initial': 0.4, 'mid': 1.0, 'late': 0.7}},
            'soybean': {'n': 85, 'p': 48, 'k': 62, 'kc': {'initial': 0.4, 'mid': 1.05, 'late': 0.75}},
            'mustard': {'n': 90, 'p': 45, 'k': 65, 'kc': {'initial': 0.45, 'mid': 1.1, 'late': 0.8}},
            'barley': {'n': 110, 'p': 55, 'k': 50, 'kc': {'initial': 0.38, 'mid': 1.02, 'late': 0.7}},
            'bajra': {'n': 95, 'p': 48, 'k': 58, 'kc': {'initial': 0.4, 'mid': 1.05, 'late': 0.75}},
            'jowar': {'n': 100, 'p': 50, 'k': 60, 'kc': {'initial': 0.4, 'mid': 1.1, 'late': 0.75}},
            'ragi': {'n': 85, 'p': 45, 'k': 55, 'kc': {'initial': 0.35, 'mid': 0.95, 'late': 0.7}},
            'oilseeds': {'n': 90, 'p': 45, 'k': 65, 'kc': {'initial': 0.45, 'mid': 1.1, 'late': 0.8}},
            'jute': {'n': 80, 'p': 40, 'k': 55, 'kc': {'initial': 0.4, 'mid': 1.0, 'late': 0.7}},
            'coconut': {'n': 500, 'p': 200, 'k': 600, 'kc': {'initial': 0.5, 'mid': 1.1, 'late': 0.9}},
            'onion': {'n': 100, 'p': 55, 'k': 80, 'kc': {'initial': 0.5, 'mid': 1.15, 'late': 0.85}},
            'potato': {'n': 110, 'p': 55, 'k': 85, 'kc': {'initial': 0.45, 'mid': 1.1, 'late': 0.8}},
            'banana': {'n': 200, 'p': 100, 'k': 300, 'kc': {'initial': 0.5, 'mid': 1.2, 'late': 1.0}},
            'spices': {'n': 90, 'p': 50, 'k': 70, 'kc': {'initial': 0.5, 'mid': 1.15, 'late': 0.85}}
        }
        
        # State-wise soil data (real values)
        self.state_soil_data = {
            'punjab': {'n': 25, 'p': 15, 'k': 20},
            'haryana': {'n': 24, 'p': 14, 'k': 19},
            'up': {'n': 23, 'p': 13, 'k': 18},
            'bihar': {'n': 20, 'p': 10, 'k': 15},
            'wb': {'n': 21, 'p': 11, 'k': 16},
            'mp': {'n': 22, 'p': 12, 'k': 17},
            'maharashtra': {'n': 18, 'p': 8, 'k': 12},
            'gujarat': {'n': 19, 'p': 9, 'k': 13},
            'rajasthan': {'n': 17, 'p': 7, 'k': 11},
            'tamilnadu': {'n': 22, 'p': 12, 'k': 18},
            'karnataka': {'n': 21, 'p': 11, 'k': 17},
            'kerala': {'n': 23, 'p': 13, 'k': 19},
            'andhra': {'n': 20, 'p': 10, 'k': 16},
            'telangana': {'n': 19, 'p': 9, 'k': 15},
            'assam': {'n': 22, 'p': 12, 'k': 18},
            'odisha': {'n': 21, 'p': 11, 'k': 17}
        }
        
        self.fertilizer_comp = {
            'urea': {'n': 0.46, 'p': 0, 'k': 0},
            'dap': {'n': 0.18, 'p': 0.46, 'k': 0},
            'mop': {'n': 0, 'p': 0, 'k': 0.60}
        }

    def get_weather(self, location: str):
        try:
            # Step 1: Get coordinates from wttr.in
            coord_url = f"http://wttr.in/{location}?format=j1"
            coord_resp = requests.get(coord_url, timeout=10)
            coord_resp.raise_for_status()
            coord_data = coord_resp.json()

            area = coord_data.get("nearest_area", [{}])[0]
            lat = float(area.get("latitude", 0))
            lon = float(area.get("longitude", 0))

            # Step 2: Get weather parameters from NASA POWER
            nasa_url = "https://power.larc.nasa.gov/api/system/timeline/daily"
            params = {
                "parameters": "T2M,RH2M,WS2M,ALLSKY_SFC_SW_DWN,PRECTOTCORR",
                "start": "20240101",
                "end": datetime.now().strftime("%Y%m%d"),
                "latitude": lat,
                "longitude": lon,
            }

            nasa_resp = requests.get(nasa_url, params=params, timeout=15)
            nasa_resp.raise_for_status()
            nasa_data = nasa_resp.json()

            # Step 3: Extract latest values
            weather_params = nasa_data["properties"]["parameter"]
            latest_data = {}
            for param, values in weather_params.items():
                latest_value = list(values.values())[-1]  # latest available
                latest_data[param] = latest_value

            # Return in your required format
            return {
                "location": location,
                "T2M": latest_data.get("T2M"),
                "RH2M": latest_data.get("RH2M"),
                "WS2M": latest_data.get("WS2M"),
                "ALLSKY_SFC_SW_DWN": latest_data.get("ALLSKY_SFC_SW_DWN"),
                "PRECTOTCORR": latest_data.get("PRECTOTCORR"),
            }

        except Exception as e:
            # Fallback values if NASA fails
            return {
                "location": location,
                "error": str(e),
                "T2M": 25.0,
                "RH2M": 60.0,
                "WS2M": 2.0,
                "ALLSKY_SFC_SW_DWN": 15.0,
                "PRECTOTCORR": 2.0,
            }


    def calculate_et0(self, weather_data):
        T = weather_data['T2M']
        RH = weather_data['RH2M']
        U2 = weather_data['WS2M']
        Rn = weather_data['ALLSKY_SFC_SW_DWN']
        
        G = 0
        P = 101.3
        
        delta = (4098 * (0.6108 * np.exp(17.27 * T / (T + 237.3)))) / ((T + 237.3) ** 2)
        gamma = 0.000665 * P
        es = 0.6108 * np.exp(17.27 * T / (T + 237.3))
        ea = (RH / 100) * es
        
        Rns = Rn * (1 - 0.23)
        Rnl = 4.903e-9 * ((T + 273.16) ** 4) * (0.34 - 0.14 * np.sqrt(ea)) * (1.35 * (Rn / 30) - 0.35)
        Rn_calc = Rns - Rnl
        
        numerator = 0.408 * delta * (Rn_calc - G) + gamma * (900 / (T + 273)) * U2 * (es - ea)
        denominator = delta + gamma * (1 + 0.34 * U2)
        et0 = numerator / denominator
        
        return max(et0, 0)

    def calculate_irrigation(self, crop_type, growth_stage, state):
        # Get weather using state name
        weather_data = self.get_weather(state)
        et0 = self.calculate_et0(weather_data)
        kc = self.crop_db[crop_type]['kc'][growth_stage]
        etc = et0 * kc
        rainfall = weather_data['PRECTOTCORR']
        irrigation_need = max(etc - rainfall, 0)

        return {
            'et0': round(et0, 2),
            'kc': kc,
            'etc': round(etc, 2),
            'rainfall': round(rainfall, 2),
            'irrigation_need': round(irrigation_need, 2)
        }

        

    def calculate_fertilizer(self, crop_type, state):
        soil_data = self.state_soil_data[state.lower()]
        req = self.crop_db[crop_type]
        
        n_gap = max(req['n'] - soil_data['n'], 0)
        p_gap = max(req['p'] - soil_data['p'], 0)
        k_gap = max(req['k'] - soil_data['k'], 0)
        
        urea = n_gap / self.fertilizer_comp['urea']['n']
        dap = p_gap / self.fertilizer_comp['dap']['p']
        mop = k_gap / self.fertilizer_comp['mop']['k']
        
        splits = {
            'basal': {'urea': urea * 0.4, 'dap': dap * 0.4, 'mop': mop * 0.4},
            'vegetative': {'urea': urea * 0.3, 'dap': dap * 0.3, 'mop': mop * 0.3},
            'reproductive': {'urea': urea * 0.3, 'dap': dap * 0.3, 'mop': mop * 0.3}
        }
        
        return {
            'soil_values': soil_data,
            'gaps': {'n': n_gap, 'p': p_gap, 'k': k_gap},
            'total_fertilizer': {
                'urea': round(urea, 2),
                'dap': round(dap, 2),
                'mop': round(mop, 2)
            },
            'splits': splits
        }

    def generate_advice(self, crop_type, growth_stage, state):
        irrigation = self.calculate_irrigation(crop_type, growth_stage, state)
        fertilizer = self.calculate_fertilizer(crop_type, state)
        
        return {
            'irrigation': irrigation,
            'fertilizer': fertilizer,
            'crop_type': crop_type,
            'state': state
        }