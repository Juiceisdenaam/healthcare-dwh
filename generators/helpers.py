import random
from datetime import date, timedelta

from .faker_instance import fake


def introduce_case_noise(value: str) -> str:
    r = random.random()
    if r < 0.10:
        return value.upper()
    if r < 0.20:
        return value.lower()
    if r < 0.30:
        return f" {value}"
    if r < 0.40:
        return f"{value} "
    return value


def introduce_name_noise(name: str) -> str:
    r = random.random()
    if r < 0.08:
        return name.upper()
    if r < 0.12:
        return name.lower()
    if r < 0.15:
        return name.replace("ij", "y")
    return name


def random_birthdate(min_age: int = 0, max_age: int = 95) -> date:
    ref = date.today() - timedelta(days=30)
    age = random.randint(min_age, max_age)
    return ref - timedelta(days=age * 365)


def generate_registration_date(birth_date: date) -> date:
    today = date.today()
    start = max(birth_date + timedelta(days=1), today - timedelta(days=25 * 365))
    if start >= today:
        return today
    return start + timedelta(days=random.randint(0, (today - start).days))


def shift_registration_date_to_other_system(registration_date: date) -> date:
    today = date.today()
    shifted = registration_date + timedelta(days=random.randint(30, 15 * 365))
    return min(shifted, today)


def generate_initials(first_name: str) -> str:
    parts = [part for part in first_name.replace("-", " ").split() if part]
    base = "".join(part[0] for part in parts).upper()
    initials = f"{base}."

    r = random.random()
    if r < 0.06:
        return initials.lower()
    if r < 0.10 and len(base) > 1:
        return f"{base[:-1]}."
    if r < 0.14:
        return initials.replace(".", "")
    if r < 0.18:
        return f"{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}."
    return initials


def generate_policy_number() -> str:
    digits = "".join(random.choices("0123456789", k=random.randint(8, 10)))
    if random.random() < 0.35:
        prefix = "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=2))
        return f"{prefix}{digits}"
    return digits


def generate_personal_id() -> str:
    return str(fake.random_number(digits=9, fix_len=True))