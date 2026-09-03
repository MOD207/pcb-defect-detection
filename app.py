from flask import Flask, request, render_template
from ultralytics import YOLO
import os
import cv2
import mysql.connector
from datetime import datetime
import uuid
from dotenv import load_dotenv


app = Flask(__name__)
model = YOLO("best.pt")
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files["image"]


        if not file or file.filename == "":
            return render_template("index.html", error="Please choose an image to upload.")


        if not allowed_file(file.filename):
            return render_template("index.html", error="Please choose a png,jpg, or jpeg format")

        unique_name = f"{uuid.uuid4().hex[:8]}_{file.filename}"
        filepath = os.path.join(UPLOAD_FOLDER,unique_name)
        file.save(filepath)

        results = model.predict(filepath, conf=0.65)
        annotated = results[0].plot()

        result_filename = "result_" + unique_name
        result_path = os.path.join(UPLOAD_FOLDER, result_filename)
        cv2.imwrite(result_path, annotated)

        detections = [
            {"class": model.names[int(box.cls)], "confidence": round(float(box.conf), 2)}
            for box in results[0].boxes
        ]

        # --- log to database ---
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO inspections (original_filename, result_filename) VALUES (%s, %s)",
            (unique_name, result_filename)
        )
        inspection_id = cursor.lastrowid

        for d in detections:
            cursor.execute(
                "INSERT INTO detections (inspection_id, defect_class, confidence) VALUES (%s, %s, %s)",
                (inspection_id, d["class"], d["confidence"])
            )

        conn.commit()
        cursor.close()
        conn.close()

        return render_template("result.html", result_image=result_filename, detections=detections)
    return render_template("index.html")
@app.route("/history")
def history():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM inspections ORDER BY timestamp DESC")
    inspections = cursor.fetchall()

    for insp in inspections:
        cursor.execute(
            "SELECT defect_class, confidence FROM detections WHERE inspection_id = %s",
            (insp["id"],)
        )
        insp["detections"] = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("history.html", inspections=inspections)

if __name__ == "__main__":
    app.run(debug=True)