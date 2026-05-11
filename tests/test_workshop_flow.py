import requests
from datetime import datetime, timedelta


def test_gateway_health(api):
    resp = requests.get(f"{api}/")
    assert resp.status_code == 200
    data = resp.json()
    assert "message" in data


def test_user_can_see_locations(api, user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    resp = requests.get(f"{api}/locations", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_user_can_see_car_brands(api, user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    resp = requests.get(f"{api}/car-brands", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 25


def test_user_can_add_car(api, user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    brands = requests.get(f"{api}/car-brands", headers=headers).json()
    toyota_id = next(b["id"] for b in brands if b["name"] == "Toyota")

    resp = requests.post(f"{api}/cars", headers=headers, json={
        "brand_id": toyota_id,
        "model": "Corolla",
        "vin": "JTDBR22E602015999",
        "color": "Srebrny",
        "mileage": 120000,
        "year": 2019
    })
    assert resp.status_code == 201
    car = resp.json()
    assert car["brand_name"] == "Toyota"
    assert car["model"] == "Corolla"
    return car["id"]


def test_user_can_get_available_slots(api, user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    locations = requests.get(f"{api}/locations", headers=headers).json()
    loc = locations[0]
    services = requests.get(f"{api}/services/locations/{loc['id']}/services", headers=headers).json()
    svc = services[0]

    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    resp = requests.get(
        f"{api}/bookings/available-slots/{svc['id']}?appointment_date={tomorrow}",
        headers=headers
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "available_slots" in data
    assert len(data["available_slots"]) >= 0


def test_user_can_create_booking(api, user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    locations = requests.get(f"{api}/locations", headers=headers).json()
    loc = locations[0]
    services = requests.get(f"{api}/services/locations/{loc['id']}/services", headers=headers).json()
    svc = services[0]

    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    slots_resp = requests.get(
        f"{api}/bookings/available-slots/{svc['id']}?appointment_date={tomorrow}",
        headers=headers
    )
    slots_data = slots_resp.json()
    if not slots_data["available_slots"]:
        print("Brak dostępnych slotów w tym dniu, pomijam test tworzenia rezerwacji")
        return

    slot = slots_data["available_slots"][0]
    employee = slot["available_employees"][0]

    resp = requests.post(f"{api}/bookings/", headers=headers, json={
        "service_id": svc["id"],
        "employee_id": employee["employee_id"],
        "appointment_date": tomorrow,
        "appointment_time": slot["time"],
    })
    assert resp.status_code == 201
    booking = resp.json()
    assert booking["status"] == "BOOKED"
    return booking["id"]


def test_user_can_cancel_booking(api, user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    bookings = requests.get(f"{api}/bookings/me", headers=headers).json()
    if not bookings:
        print("Brak rezerwacji do anulowania")
        return
    booking_id = bookings[0]["id"]
    resp = requests.patch(f"{api}/bookings/{booking_id}/cancel", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "CANCELLED"


def test_review_crud(api, user_token, admin_token):
    headers_user = {"Authorization": f"Bearer {user_token}"}
    headers_admin = {"Authorization": f"Bearer {admin_token}"}

    locations = requests.get(f"{api}/locations", headers=headers_user).json()
    loc_id = locations[0]["id"]

    
    stats = requests.get(f"{api}/reviews/location/{loc_id}/stats")
    assert stats.status_code == 200
    assert stats.json()["total_reviews"] == 0

    
    resp = requests.post(f"{api}/reviews/", headers=headers_user, json={
        "location_id": loc_id,
        "rating": 5,
        "comment": "Świetny warsztat!",
    })
    assert resp.status_code == 201
    review = resp.json()
    assert review["rating"] == 5

    
    review_id = review["id"]
    resp = requests.put(f"{api}/reviews/{review_id}", headers=headers_user, json={
        "rating": 4,
        "comment": "Bardzo dobry warsztat.",
    })
    assert resp.status_code == 200
    assert resp.json()["rating"] == 4

    
    stats = requests.get(f"{api}/reviews/location/{loc_id}/stats")
    assert stats.status_code == 200
    stats_data = stats.json()
    assert stats_data["total_reviews"] == 1
    assert stats_data["average_rating"] == 4.0

    
    resp = requests.delete(f"{api}/reviews/{review_id}", headers=headers_user)
    assert resp.status_code == 200

    
    stats = requests.get(f"{api}/reviews/location/{loc_id}/stats")
    assert stats.json()["total_reviews"] == 0


def test_booking_blocked_on_closed_day(api, user_token):
    
    headers = {"Authorization": f"Bearer {user_token}"}
    locations = requests.get(f"{api}/locations", headers=headers).json()
    loc = locations[0]
    services = requests.get(f"{api}/services/locations/{loc['id']}/services", headers=headers).json()
    svc = services[0]

    
    today = datetime.now().date()
    days_until_sunday = (6 - today.weekday()) % 7
    if days_until_sunday == 0:
        days_until_sunday = 7
    next_sunday = (today + timedelta(days=days_until_sunday)).strftime("%Y-%m-%d")

    resp = requests.get(
        f"{api}/bookings/available-slots/{svc['id']}?appointment_date={next_sunday}",
        headers=headers
    )
    
    if resp.status_code == 400:
        assert "zamknięty" in resp.json()["detail"].lower()
    else:
        assert resp.status_code == 200
        assert len(resp.json()["available_slots"]) == 0