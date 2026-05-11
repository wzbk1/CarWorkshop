import pytest
import requests
import time

API_URL = "http://127.0.0.1:8080"


@pytest.fixture(scope="session")
def api():
    for _ in range(30):
        try:
            requests.get(f"{API_URL}/", timeout=3)
            break
        except Exception:
            time.sleep(1)
    return API_URL


@pytest.fixture(scope="session")
def admin_token(api):
    resp = requests.post(f"{api}/auth/login", json={
        "email": "admin@carworkshop.pl",
        "password": "Admin123!"
    })
    assert resp.status_code == 200
    return resp.json()["access_token"]


@pytest.fixture(scope="session")
def user_token(api):
    
    resp = requests.post(f"{api}/auth/login", json={
        "email": "jan@example.com",
        "password": "User123!"
    })
    if resp.status_code == 401:
        requests.post(f"{api}/auth/register", json={
            "first_name": "Jan",
            "last_name": "Kowalski",
            "email": "jan@example.com",
            "password": "User123!"
        })
        resp = requests.post(f"{api}/auth/login", json={
            "email": "jan@example.com",
            "password": "User123!"
        })
    assert resp.status_code == 200
    return resp.json()["access_token"]