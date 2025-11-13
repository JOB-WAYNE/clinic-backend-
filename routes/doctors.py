# routes/doctors.py
from flask import Blueprint, request, jsonify
from extensions import db
from models.doctors import Doctor
from models.patients import Patient
from models.appointments import Appointment
from models.prescriptions import Prescription
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from sqlalchemy.orm import joinedload

doctor_bp = Blueprint('doctors', __name__)

# GET ALL DOCTORS — FOR PATIENT BOOKING
@doctor_bp.route('/doctors', methods=['GET'])
def get_all_doctors():
    doctors = Doctor.query.all()
    return jsonify([d.to_dict() for d in doctors]), 200

# REGISTER DOCTOR
@doctor_bp.route('/doctors/register', methods=['POST'])
def register_doctor():
    data = request.get_json()
    required = ['full_name', 'email', 'password', 'specialty', 'phone']
    for field in required:
        if field not in data or not data[field]:
            return jsonify({"error": f"'{field}' required"}), 400

    if Doctor.query.filter_by(email=data['email']).first():
        return jsonify({"error": "Email exists"}), 400
    if Doctor.query.filter_by(phone=data['phone']).first():
        return jsonify({"error": "Phone exists"}), 400

    doctor = Doctor(**data)
    db.session.add(doctor)
    db.session.commit()
    return jsonify({"message": "Registered", "doctor": doctor.to_dict()}), 201

# LOGIN DOCTOR
@doctor_bp.route('/doctors/login', methods=['POST'])
def login_doctor():
    data = request.get_json()
    if not data.get('email') or not data.get('password'):
        return jsonify({"error": "Email and password required"}), 400

    doctor = Doctor.query.filter_by(email=data['email']).first()
    if doctor and doctor.check_password(data['password']):
        token = create_access_token(identity=doctor.id)
        return jsonify({
            "message": "Login successful",
            "token": token,
            "doctor": doctor.to_dict()
        }), 200
    return jsonify({"error": "Invalid credentials"}), 401

# UPDATE AVAILABILITY
@doctor_bp.route('/doctors/status', methods=['PUT'])
@jwt_required()
def update_status():
    doctor_id = get_jwt_identity()
    doctor = Doctor.query.get(doctor_id)
    if not doctor:
        return jsonify({"error": "Not found"}), 404

    data = request.get_json()
    if 'is_available' not in data or not isinstance(data['is_available'], bool):
        return jsonify({"error": "'is_available' must be boolean"}), 400

    doctor.is_available = data['is_available']
    db.session.commit()
    return jsonify({"message": "Status updated", "doctor": doctor.to_dict()}), 200

# VIEW DOCTOR'S APPOINTMENTS
@doctor_bp.route('/doctors/appointments', methods=['GET'])
@jwt_required()
def get_doctor_appointments():
    doctor_id = get_jwt_identity()
    appts = Appointment.query.filter_by(doctor_id=doctor_id).order_by(Appointment.date.desc()).all()
    return jsonify({"appointments": [appt.to_dict() for appt in appts]}), 200

# VIEW ASSIGNED PATIENTS — FIXED: LATEST APPOINTMENT
@doctor_bp.route('/doctors/patients', methods=['GET'])
@jwt_required()
def view_patients():
    doctor_id = get_jwt_identity()
    
    # Get ALL appointments for this doctor
    appointments = Appointment.query.filter_by(doctor_id=doctor_id).all()
    if not appointments:
        return jsonify({"patients": []}), 200

    # Group by patient
    patients_map = {}
    for appt in appointments:
        pid = appt.patient.id
        if pid not in patients_map:
            patients_map[pid] = {
                "patient": appt.patient.to_dict(),
                "appointments": []
            }
        patients_map[pid]["appointments"].append(appt)

    # Get LATEST appointment per patient
    result = []
    for pid, data in patients_map.items():
        latest_appt = max(data["appointments"], key=lambda x: x.date)
        result.append({
            "patient": data["patient"],
            "latest_appointment": latest_appt.to_dict()
        })

    return jsonify({"patients": result}), 200

# PRESCRIBE DRUGS — ALREADY CORRECT
@doctor_bp.route('/doctors/prescribe', methods=['POST'])
@jwt_required()
def prescribe_drugs():
    doctor_id = get_jwt_identity()
    data = request.get_json()

    required = ['patient_id', 'appointment_id', 'drug_name', 'dosage']
    for field in required:
        if field not in data or not data[field]:
            return jsonify({"error": f"'{field}' is required"}), 400

    if not Doctor.query.get(doctor_id):
        return jsonify({"error": "Doctor not found"}), 404

    appt = Appointment.query.get(data['appointment_id'])
    if not appt:
        return jsonify({"error": "Appointment not found"}), 404
    if appt.doctor_id != doctor_id:
        return jsonify({"error": "You can only prescribe for your own appointments"}), 403

    prescription = Prescription(
        doctor_id=doctor_id,
        patient_id=data['patient_id'],
        appointment_id=data['appointment_id'],
        drug_name=data['drug_name'],
        dosage=data['dosage'],
        instructions=data.get('instructions', '')
    )
    db.session.add(prescription)
    db.session.commit()

    return jsonify({
        "message": "Prescription created",
        "prescription": prescription.to_dict()
    }), 201