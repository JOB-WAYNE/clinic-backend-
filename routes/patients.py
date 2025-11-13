# routes/patients.py
from flask import Blueprint, request, jsonify
from extensions import db
from models.patients import Patient
from models.appointments import Appointment
from models.prescriptions import Prescription
from models.doctors import Doctor
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import datetime

patient_bp = Blueprint('patients', __name__)

# REGISTER
@patient_bp.route('/patients/register', methods=['POST'])
def register_patient():
    data = request.get_json()
    required = ['full_name', 'email', 'password', 'phone']
    if not all(k in data for k in required):
        return jsonify({"error": "Missing fields"}), 400

    if Patient.query.filter_by(email=data['email']).first():
        return jsonify({"error": "Email exists"}), 400
    if Patient.query.filter_by(phone=data['phone']).first():
        return jsonify({"error": "Phone exists"}), 400

    patient = Patient(**data)
    db.session.add(patient)
    db.session.commit()
    return jsonify({
        "message": "Registered",
        "patient": patient.to_dict()
    }), 201


# LOGIN
@patient_bp.route('/patients/login', methods=['POST'])
def login_patient():
    data = request.get_json()
    if not data.get('email') or not data.get('password'):
        return jsonify({"error": "Email and password required"}), 400

    patient = Patient.query.filter_by(email=data['email']).first()
    if patient and patient.check_password(data['password']):
        token = create_access_token(identity=patient.id)
        return jsonify({
            "message": "Login successful",
            "token": token,
            "patient": patient.to_dict()
        }), 200
    return jsonify({"error": "Invalid credentials"}), 401


# BOOK APPOINTMENT
@patient_bp.route('/patients/appointments', methods=['POST'])
@jwt_required()
def book_appointment():
    patient_id = get_jwt_identity()
    data = request.get_json()

    if not data.get('doctor_id') or not data.get('date'):
        return jsonify({"error": "doctor_id and date required"}), 400

    if not Doctor.query.get(data['doctor_id']):
        return jsonify({"error": "Doctor not found"}), 404

    try:
        appt_date = datetime.strptime(data['date'], '%Y-%m-%d %H:%M')
    except ValueError:
        return jsonify({"error": "Invalid date format"}), 400

    appt = Appointment(
        patient_id=patient_id,
        doctor_id=data['doctor_id'],
        date=appt_date,
        reason=data.get('reason', ''),
        status='Approved'
    )
    db.session.add(appt)
    db.session.commit()

    # USE to_dict() → NO parse error, NO ** unpacking
    return jsonify({
        "message": "Appointment booked",
        "appointment": appt.to_dict()
    }), 201


# VIEW APPOINTMENTS
@patient_bp.route('/patients/appointments', methods=['GET'])
@jwt_required()
def get_my_appointments():
    patient_id = get_jwt_identity()
    appts = Appointment.query.filter_by(patient_id=patient_id).all()
    return jsonify({
        "appointments": [a.to_dict() for a in appts]
    }), 200


# VIEW PRESCRIPTIONS
@patient_bp.route('/patients/prescriptions', methods=['GET'])
@jwt_required()
def get_my_prescriptions():
    patient_id = get_jwt_identity()
    pres = Prescription.query.filter_by(patient_id=patient_id).all()
    return jsonify({
        "prescriptions": [p.to_dict() for p in pres]
    }), 200