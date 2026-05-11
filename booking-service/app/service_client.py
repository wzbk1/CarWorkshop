import os
import requests
from dotenv import load_dotenv

load_dotenv()

SERVICE_MANAGEMENT_URL = os.getenv("SERVICE_MANAGEMENT_URL")


def _get_base_url() -> str:
    if not SERVICE_MANAGEMENT_URL:
        raise ValueError("Brak SERVICE_MANAGEMENT_URL w pliku .env")
    return SERVICE_MANAGEMENT_URL.rstrip("/")


def get_service_by_id(service_id: int) -> dict | None:
    url = f"{_get_base_url()}/services/{service_id}"
    try:
        response = requests.get(url, timeout=5)
    except requests.RequestException as e:
        raise ConnectionError(f"Nie udało się połączyć z service-management: {str(e)}")
    if response.status_code == 404:
        return None
    if not response.ok:
        raise ConnectionError(f"Błąd pobierania usługi. Status: {response.status_code}")
    return response.json()


def get_employees_for_service(service_id: int) -> list[dict]:
    url = f"{_get_base_url()}/employees/services/{service_id}/employees?active_only=true"
    try:
        response = requests.get(url, timeout=5)
    except requests.RequestException as e:
        raise ConnectionError(f"Nie udało się połączyć z service-management: {str(e)}")
    if response.status_code == 404:
        return []
    if not response.ok:
        raise ConnectionError(f"Błąd pobierania pracowników. Status: {response.status_code}")
    return response.json()


def get_business_hours_for_location_and_day(location_id: int, day_of_week: int) -> dict | None:
    url = f"{_get_base_url()}/business-hours/locations/{location_id}/business-hours/{day_of_week}"
    try:
        response = requests.get(url, timeout=5)
    except requests.RequestException as e:
        raise ConnectionError(f"Nie udało się połączyć z service-management: {str(e)}")
    if response.status_code == 404:
        return None
    if not response.ok:
        raise ConnectionError(f"Błąd pobierania godzin pracy. Status: {response.status_code}")
    return response.json()


def get_location_exception_for_date(location_id: int, exception_date: str) -> dict | None:
    url = f"{_get_base_url()}/location-exceptions/locations/{location_id}/exceptions/{exception_date}"
    try:
        response = requests.get(url, timeout=5)
    except requests.RequestException as e:
        raise ConnectionError(f"Nie udało się połączyć z service-management: {str(e)}")
    if response.status_code == 404:
        return None
    if not response.ok:
        raise ConnectionError(f"Błąd pobierania wyjątku. Status: {response.status_code}")
    return response.json()


def get_employee_absence_for_date(employee_id: int, absence_date: str) -> dict | None:
    url = f"{_get_base_url()}/employee-absences/employees/{employee_id}/absences/{absence_date}"
    try:
        response = requests.get(url, timeout=5)
    except requests.RequestException as e:
        raise ConnectionError(f"Nie udało się połączyć z service-management: {str(e)}")
    if response.status_code == 404:
        return None
    if not response.ok:
        raise ConnectionError(f"Błąd pobierania nieobecności. Status: {response.status_code}")
    return response.json()


def get_employee_full_name(employee_id: int) -> str:
    url = f"{_get_base_url()}/employees/{employee_id}"
    try:
        response = requests.get(url, timeout=5)
    except requests.RequestException as e:
        raise ConnectionError(f"Nie udało się połączyć z service-management: {str(e)}")
    if not response.ok:
        raise ConnectionError(f"Błąd pobierania pracownika. Status: {response.status_code}")
    data = response.json()
    return f"{data.get('first_name', '')} {data.get('last_name', '')}".strip()



def get_location_by_id(location_id: int) -> dict | None:
    url = f"{_get_base_url()}/locations/{location_id}"
    try:
        response = requests.get(url, timeout=5)
    except requests.RequestException as e:
        raise ConnectionError(f"Nie udało się połączyć z service-management: {str(e)}")
    if response.status_code == 404:
        return None
    if not response.ok:
        raise ConnectionError(f"Błąd pobierania warsztatu. Status: {response.status_code}")
    return response.json()


def validate_service_payload(service: dict) -> None:
    required_fields = ["id", "location_id", "name", "duration_minutes", "is_active"]
    missing = [f for f in required_fields if f not in service]
    if missing:
        raise ValueError(f"Dane usługi niekompletne. Brak pól: {', '.join(missing)}")


def validate_employee_payload(employee: dict) -> None:
    required_fields = ["id", "first_name", "last_name", "is_active"]
    missing = [f for f in required_fields if f not in employee]
    if missing:
        raise ValueError(f"Dane pracownika niekompletne. Brak pól: {', '.join(missing)}")


def validate_business_hours_payload(hours: dict) -> None:
    if "is_closed" not in hours:
        raise ValueError("Dane godzin pracy niekompletne")


def validate_location_exception_payload(exception: dict) -> None:
    if "is_closed" not in exception:
        raise ValueError("Dane wyjątku niekompletne")


def validate_employee_absence_payload(absence: dict) -> None:
    required_fields = ["id", "employee_id", "absence_date"]
    missing = [f for f in required_fields if f not in absence]
    if missing:
        raise ValueError(f"Dane nieobecności niekompletne. Brak pól: {', '.join(missing)}")