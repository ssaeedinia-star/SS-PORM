import os
import boto3
from werkzeug.utils import secure_filename
from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__, static_folder=".")
CORS(app)
# Liara Object Storage
LIARA_ENDPOINT_URL = os.environ.get("LIARA_ENDPOINT_URL")
LIARA_ACCESS_KEY = os.environ.get("LIARA_ACCESS_KEY")
LIARA_SECRET_KEY = os.environ.get("LIARA_SECRET_KEY")
LIARA_BUCKET_NAME = os.environ.get("LIARA_BUCKET_NAME")

s3 = boto3.client(
    "s3",
    endpoint_url=LIARA_ENDPOINT_URL,
    aws_access_key_id=LIARA_ACCESS_KEY,
    aws_secret_access_key=LIARA_SECRET_KEY
)
database_url = os.environ.get("DATABASE_URL", "sqlite:///ss_porm.db")
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_code = db.Column(db.String(100), unique=True, nullable=False)
    data = db.Column(db.JSON, nullable=False)


with app.app_context():
    db.create_all()
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@app.route("/")
def home():
    return send_from_directory(".", "index.html")


@app.route("/api/patients", methods=["POST"])
def save_patient():
    payload = request.get_json(silent=True)

    if not payload:
        return jsonify({"error": "No data received"}), 400

    patient_code = payload.get("patient_code")

    if not patient_code:
        return jsonify({"error": "patient_code is required"}), 400

    patient = Patient.query.filter_by(patient_code=patient_code).first()

    if patient:
        patient.data = payload
    else:
        patient = Patient(
            patient_code=patient_code,
            data=payload
        )
        db.session.add(patient)

    db.session.commit()

    return jsonify({
        "success": True,
        "patient_code": patient_code
    })


@app.route("/api/patients/<patient_code>", methods=["GET"])
def get_patient(patient_code):

    patient = Patient.query.filter_by(
        patient_code=patient_code
    ).first()

    if not patient:
        return jsonify({"error": "Patient not found"}), 404

    return jsonify(patient.data)

@app.route("/api/patients", methods=["GET"])
def list_patients():
    patients = Patient.query.order_by(Patient.id.desc()).all()

    result = []
    for patient in patients:
        data = patient.data or {}
        result.append({
            "patient_code": patient.patient_code,
            "patient_name": data.get("patient_name", ""),
            "age": data.get("age", ""),
            "sex": data.get("sex", ""),
            "diagnosis": data.get("diagnosis", "")
        })

    return jsonify(result)
@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "service": "SS-PORM"
    })


@app.route("/api/upload/<patient_code>", methods=["POST"])
def upload_file(patient_code):
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if not file or not file.filename:
        return jsonify({"error": "No file selected"}), 400
    patient_code_safe = secure_filename(patient_code)
filename = secure_filename(file.filename)
object_key = f"{patient_code_safe}/{filename}"

    s3.upload_fileobj(
        file,
        LIARA_BUCKET_NAME,
        object_key,
        ExtraArgs={"ContentType":
        file.content_type or "application/octet-stream"}
    )

    return jsonify({
        "status": "ok",
        "filename": filename
    })
@app.route("/api/files/<patient_code>", methods=["GET"])
def list_patient_files(patient_code):
    patient_folder = os.path.join(
        app.config["UPLOAD_FOLDER"],
        secure_filename(patient_code)
    )

    if not os.path.isdir(patient_folder):
        return jsonify({"patient_code": patient_code, "files": []})

    files = os.listdir(patient_folder)

    return jsonify({
        "patient_code": patient_code,
        "files": files
    })
@app.route("/api/files/<patient_code>/<filename>", methods=["GET"])
def get_patient_file(patient_code, filename):
    patient_folder = os.path.join(
        app.config["UPLOAD_FOLDER"],
        secure_filename(patient_code)
    )
    return send_from_directory(
        patient_folder,
        secure_filename(filename)
    )




if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
