import csv
import os
from datetime import datetime

from app.database import get_employee_by_id

ACCESS_LOG_FILE = os.path.join(os.path.dirname(__file__), "..", "access_log.csv")


def log_access(employee_id: str, area: str, recognized_name: str, allowed: bool):
    timestamp = datetime.utcnow().isoformat()
    row = [timestamp, employee_id, recognized_name, area, "ALLOWED" if allowed else "DENIED"]
    file_exists = os.path.isfile(ACCESS_LOG_FILE)

    with open(ACCESS_LOG_FILE, "a", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(["timestamp", "employee_id", "name", "area", "status"])
        writer.writerow(row)

    print(f"{timestamp} - {recognized_name} ({employee_id}) access {row[4]} for {area}")


def check_access(employee_id: str, area: str):
    employee = get_employee_by_id(employee_id)
    if not employee:
        return False, "Unknown employee"
    allowed = employee.allowed_area.lower() == area.lower()
    return allowed, employee.name


def notify_admin(employee_id: str, name: str, area: str):
    message = (
        f"ALERT: {name} ({employee_id}) attempted entry in unauthorized area {area} at "
        f"{datetime.utcnow().isoformat()}"
    )
    print(message)
    # TODO: replace with email/SMS/push notification
    return message
