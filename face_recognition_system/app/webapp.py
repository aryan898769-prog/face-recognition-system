import os
from collections import deque
from datetime import datetime

import cv2
import numpy as np
from flask import Flask, render_template, request, redirect, url_for, flash, Response, jsonify
from werkzeug.utils import secure_filename

from app.access_control import check_access, log_access, notify_admin
from app.database import add_employee, get_all_employees
from app.face_model import image_to_embedding
from app.recognize import detect_faces, load_employee_embeddings, TOLERANCE
from app.train import generate_embeddings

BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "..", "data", "employees")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

app = Flask(__name__)
app.secret_key = "change-this-secret"
app.config["UPLOAD_FOLDER"] = DATA_DIR
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

alerts = deque(maxlen=100)


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def append_alert(message: str) -> None:
    alerts.appendleft({
        "timestamp": datetime.utcnow().isoformat(),
        "message": message,
    })


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        employee_id = request.form.get("employee_id", "").strip()
        name = request.form.get("name", "").strip()
        allowed_area = request.form.get("allowed_area", "").strip()
        files = request.files.getlist("photos")

        if not employee_id or not name or not allowed_area:
            flash("Employee ID, name, and allowed area are required.")
            return redirect(url_for("register"))

        if not files or all(f.filename == "" for f in files):
            flash("Please upload at least one face image.")
            return redirect(url_for("register"))

        employee_folder = os.path.join(DATA_DIR, secure_filename(employee_id))
        os.makedirs(employee_folder, exist_ok=True)

        saved_files = 0
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(employee_folder, filename))
                saved_files += 1

        if saved_files == 0:
            flash("No valid image files were uploaded. Use PNG or JPG.")
            return redirect(url_for("register"))

        add_employee(employee_id=employee_id, name=name, allowed_area=allowed_area)
        flash(f"Employee {name} ({employee_id}) registered with {saved_files} photos.")
        return redirect(url_for("index"))

    return render_template("register.html")


@app.route("/admin")
def admin_dashboard():
    area = request.args.get("area", "Lobby")
    employee_embeddings = {}
    try:
        employee_embeddings = load_employee_embeddings()
    except FileNotFoundError:
        flash("No embeddings found. Run training before monitoring.")

    employees = get_all_employees()
    areas = sorted({employee.allowed_area for employee in employees})

    return render_template(
        "monitor.html",
        area=area,
        employee_count=len(employee_embeddings),
        employees=employees,
        areas=areas,
        alerts=list(alerts),
    )


@app.route("/video_feed")
def video_feed():
    area = request.args.get("area", "Lobby")
    return Response(
        generate_camera_frames(area),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )


@app.route("/admin/alerts")
def admin_alerts():
    return jsonify(list(alerts))


@app.route("/admin/retrain", methods=["POST"])
def admin_retrain():
    try:
        generate_embeddings()
        flash("Retraining complete. Embeddings have been updated.")
    except Exception as exc:
        flash(f"Retraining failed: {exc}")
    return redirect(url_for("admin_dashboard", area=request.form.get("area", "Lobby")))


@app.route("/admin/clear_alerts", methods=["POST"])
def clear_alerts():
    alerts.clear()
    return jsonify({"status": "cleared"})


def generate_camera_frames(area: str):
    employee_embeddings = load_employee_embeddings()
    if not employee_embeddings:
        yield b""
        return

    video_capture = cv2.VideoCapture(0)
    if not video_capture.isOpened():
        raise RuntimeError("Could not open camera")

    while True:
        ret, frame = video_capture.read()
        if not ret:
            break

        detections = detect_faces(frame)
        for top, right, bottom, left in detections:
            face_image = frame[top:bottom, left:right]
            if face_image.size == 0:
                continue

            current_embedding = image_to_embedding(face_image)

            best_match_id = None
            best_distance = float("inf")
            for emp_id, emp_embedding in employee_embeddings.items():
                distance = np.linalg.norm(current_embedding - emp_embedding)
                if distance < best_distance:
                    best_distance = distance
                    best_match_id = emp_id

            match_found = best_distance <= TOLERANCE
            if match_found:
                allowed, name = check_access(best_match_id, area)
                log_access(best_match_id, area, name, allowed)
                if not allowed:
                    message = notify_admin(best_match_id, name, area)
                    append_alert(message)
                label = f"{name} (dist: {best_distance:.2f}) {'OK' if allowed else 'DENIED'}"
            else:
                message = (
                    f"ALERT: Unknown person detected in {area} at {datetime.utcnow().isoformat()}"
                )
                append_alert(message)
                label = f"Unknown (dist: {best_distance:.2f})"

            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(
                frame,
                label,
                (left, top - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2,
            )

        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    video_capture.release()


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
