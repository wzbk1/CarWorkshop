from datetime import datetime, date, time, timedelta

SLOT_MINUTES = 30
VALID_MINUTES = {0, 30}


def parse_booking_datetime(appointment_date: str, appointment_time: str) -> tuple[date, time, datetime]:
    try:
        parsed_date = datetime.strptime(appointment_date, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("Nieprawidłowy format daty. Użyj YYYY-MM-DD.")
    try:
        parsed_time = datetime.strptime(appointment_time, "%H:%M").time()
    except ValueError:
        raise ValueError("Nieprawidłowy format godziny. Użyj HH:MM.")
    combined = datetime.combine(parsed_date, parsed_time)
    return parsed_date, parsed_time, combined


def get_day_of_week(appointment_date: str) -> int:
    try:
        parsed_date = datetime.strptime(appointment_date, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("Nieprawidłowy format daty. Użyj YYYY-MM-DD.")
    return parsed_date.weekday()


def validate_booking_datetime_basic(appointment_date: str, appointment_time: str) -> None:
    _, parsed_time, combined = parse_booking_datetime(appointment_date, appointment_time)
    now = datetime.now()
    if combined <= now:
        raise ValueError("Nie można zarezerwować wizyty w przeszłości.")
    if parsed_time.minute not in VALID_MINUTES:
        raise ValueError("Rezerwacje są dostępne tylko co 30 minut, np. 08:00, 08:30, 09:00.")


def generate_daily_slots(open_time: str, close_time: str, lunch_start: str | None = None, lunch_end: str | None = None) -> list[str]:
    
    slots = []
    try:
        current = datetime.strptime(open_time, "%H:%M")
        end = datetime.strptime(close_time, "%H:%M")
    except ValueError:
        raise ValueError("Nieprawidłowe godziny pracy. Użyj HH:MM.")

    lunch_start_dt = None
    lunch_end_dt = None
    if lunch_start and lunch_end:
        try:
            lunch_start_dt = datetime.strptime(lunch_start, "%H:%M")
            lunch_end_dt = datetime.strptime(lunch_end, "%H:%M")
        except ValueError:
            pass

    while current < end:
        slot_time = current.strftime("%H:%M")
        
        if lunch_start_dt and lunch_end_dt and lunch_start_dt <= current < lunch_end_dt:
            current += timedelta(minutes=SLOT_MINUTES)
            continue
        slots.append(slot_time)
        current += timedelta(minutes=SLOT_MINUTES)
    return slots


def filter_future_slots(appointment_date: str, slots: list[str]) -> list[str]:
    today = datetime.now().date()
    try:
        parsed_date = datetime.strptime(appointment_date, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("Nieprawidłowy format daty. Użyj YYYY-MM-DD.")
    if parsed_date < today:
        return []
    if parsed_date > today:
        return slots
    now = datetime.now()
    available = []
    for slot in slots:
        slot_time = datetime.strptime(slot, "%H:%M").time()
        combined = datetime.combine(parsed_date, slot_time)
        if combined > now:
            available.append(slot)
    return available


def get_required_slots(duration_minutes: int) -> int:
    if duration_minutes <= 0:
        raise ValueError("Czas trwania usługi musi być większy od zera.")
    slots = duration_minutes // SLOT_MINUTES
    if duration_minutes % SLOT_MINUTES != 0:
        slots += 1
    return slots


def add_minutes_to_time_str(time_str: str, minutes: int) -> str:
    current = datetime.strptime(time_str, "%H:%M")
    new_time = current + timedelta(minutes=minutes)
    return new_time.strftime("%H:%M")


def build_time_window(start_time: str, duration_minutes: int) -> list[str]:
    required_slots = get_required_slots(duration_minutes)
    slots = []
    current_time = start_time
    for _ in range(required_slots):
        slots.append(current_time)
        current_time = add_minutes_to_time_str(current_time, SLOT_MINUTES)
    return slots


def ranges_overlap(start_a: str, duration_a: int, start_b: str, duration_b: int) -> bool:
    a_start = datetime.strptime(start_a, "%H:%M")
    a_end = a_start + timedelta(minutes=duration_a)
    b_start = datetime.strptime(start_b, "%H:%M")
    b_end = b_start + timedelta(minutes=duration_b)
    return a_start < b_end and b_start < a_end


def can_service_fit_in_schedule(start_time: str, duration_minutes: int, close_time: str, lunch_start: str | None = None, lunch_end: str | None = None) -> bool:
    end_time = add_minutes_to_time_str(start_time, duration_minutes)
    if end_time > close_time:
        return False
    if lunch_start and lunch_end:
        start_dt = datetime.strptime(start_time, "%H:%M")
        end_dt = datetime.strptime(end_time, "%H:%M")
        lunch_start_dt = datetime.strptime(lunch_start, "%H:%M")
        lunch_end_dt = datetime.strptime(lunch_end, "%H:%M")
        if start_dt < lunch_end_dt and end_dt > lunch_start_dt:
            return False
    return True