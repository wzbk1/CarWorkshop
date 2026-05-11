import requests
import time
import os

API_URL = "http://63.177.137.197"

LOCATIONS = [
    {"name": "AutoSerwis Premium", "city": "Warszawa", "address": "ul. Warszawska 10", "description": "Serwis aut luksusowych i sportowych."},
    {"name": "Japan Motors Serwis", "city": "Kraków", "address": "ul. Japońska 5", "description": "Specjaliści od marek japońskich."},
    {"name": "EuroAuto Naprawa", "city": "Gdańsk", "address": "ul. Europejska 1", "description": "Kompleksowa naprawa aut europejskich."},
    {"name": "Italian Style Garage", "city": "Wrocław", "address": "ul. Włoska 12", "description": "Pasja do włoskiej motoryzacji."},
    {"name": "American Muscle Service", "city": "Poznań", "address": "ul. Teksańska 8", "description": "Naprawa i tuning aut z USA."}
]

BRANDS = [
    "Audi", "BMW", "Mercedes-Benz", "Porsche", "Volkswagen",
    "Toyota", "Honda", "Nissan", "Mazda", "Subaru", "Lexus",
    "Fiat", "Alfa Romeo", "Ferrari", "Lamborghini", "Maserati",
    "Ford", "Chevrolet", "Dodge", "Jeep", "Tesla",
    "Renault", "Peugeot", "Citroen", "Volvo", "Skoda", "Hyundai", "Kia"
]

SERVICES = [
    {"name": "Przegląd okresowy", "duration_minutes": 60, "price": 200},
    {"name": "Wymiana oleju i filtrów", "duration_minutes": 45, "price": 150},
    {"name": "Wymiana klocków hamulcowych", "duration_minutes": 90, "price": 250},
    {"name": "Diagnostyka komputerowa", "duration_minutes": 30, "price": 100}
]

FIRST_NAMES = ["Jan", "Adam", "Piotr", "Tomasz", "Krzysztof", "Michał", "Marcin", "Jakub", "Marek", "Łukasz", "Kamil", "Mateusz", "Dawid"]
LAST_NAMES = ["Kowalski", "Nowak", "Wiśniewski", "Wójcik", "Kowalczyk", "Kamiński", "Lewandowski", "Zieliński", "Szymański", "Woźniak"]
SPECIALIZATIONS = ["Silniki", "Elektronika", "Klimatyzacja", "Zawieszenie", "Układ hamulcowy", "Diagnostyka"]

def api_request(method, path, token=None, json=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        url = f"{API_URL}{path}"
        response = requests.request(method=method, url=url, headers=headers, json=json, timeout=10)
        if response.status_code >= 400:
            print(f"  [ERROR] {method} {path} -> {response.status_code}: {response.text}")
            return None
        return response.json() if response.text else {}
    except Exception as e:
        print(f"  [CRITICAL] {method} {path} -> {e}")
        return None

def run():
    print("=== CAR WORKSHOP SEEDER 6.0 ===")
    
    
    auth_resp = requests.post(f"{API_URL}/auth/login", json={"email": "admin@carworkshop.pl", "password": "Admin123!"})
    if auth_resp.status_code != 200:
        print("Błąd logowania admina!")
        return
    token = auth_resp.json()["access_token"]

    print("\n1. CZYSZCZENIE...")
    cars = api_request("GET", "/cars/", token=token) or []
    for c in cars: api_request("DELETE", f"/cars/{c['id']}", token=token)
    
    locs = api_request("GET", "/locations/", token=token) or []
    for l in locs: api_request("DELETE", f"/locations/{l['id']}", token=token)
    
    brands = api_request("GET", "/car-brands/", token=token) or []
    for b in brands: api_request("DELETE", f"/car-brands/{b['id']}", token=token)
    print("  Czyszczenie zakończone.")

    print("\n2. TWORZENIE MAREK...")
    brand_map = {}
    for b_name in BRANDS:
        res = api_request("POST", "/car-brands/", token=token, json={"name": b_name})
        if res: brand_map[b_name] = res["id"]

    print("\n3. TWORZENIE WARSZTATÓW...")
    for loc_data in LOCATIONS:
        new_loc = api_request("POST", "/locations/", token=token, json=loc_data)
        if not new_loc: continue
        l_id = new_loc["id"]
        print(f"  + Warsztat: {loc_data['name']} (ID: {l_id})")

        
        for i in range(7):
            api_request("POST", f"/business-hours/locations/{l_id}/business-hours", token=token, json={
                "day_of_week": i,
                "open_time": "08:00",
                "close_time": "20:00",
                "is_closed": i == 6
            })


        
        for b_name in brand_map:
            api_request("POST", f"/car-brands/locations/{l_id}/brands?brand_id={brand_map[b_name]}", token=token)

        
        s_ids = []
        for s_data in SERVICES:
            s_res = api_request("POST", f"/services/locations/{l_id}/services", token=token, json=s_data)
            if s_res: s_ids.append(s_res["id"])

        
        for mi in range(2):
            
            loc_idx = LOCATIONS.index(loc_data)
            fn = FIRST_NAMES[(loc_idx * 2 + mi) % len(FIRST_NAMES)]
            ln = LAST_NAMES[(loc_idx * 2 + mi) % len(LAST_NAMES)]
            sp = SPECIALIZATIONS[(loc_idx * 2 + mi) % len(SPECIALIZATIONS)]
            m_data = {
                "first_name": fn,
                "last_name": ln,
                "specialization": sp
            }
            m_res = api_request("POST", f"/employees/locations/{l_id}/employees", token=token, json=m_data)
            if m_res:
                emp_id = m_res["id"]
                
                import random
                assigned_sids = random.sample(s_ids, min(len(s_ids), random.randint(2, 3)))
                for sid in assigned_sids:
                    api_request("POST", f"/employees/{emp_id}/services", token=token, json={"service_id": sid})

    print("\n=== SEEDOWANIE ZAKOŃCZONE POMYŚLNIE ===")

if __name__ == "__main__":
    run()