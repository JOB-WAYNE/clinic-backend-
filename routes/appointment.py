# routes/appointments.py
from flask import Blueprint, request, jsonify
from extensions import db
from models.appointments import Appointment
from models.doctors import Doctor  # ← For doctor validation
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

appointment_bp = Blueprint('appointments', __name__)

# BOOK APPOINTMENT
@appointment_bp.route('/appointments', methods=['POST'])
@jwt_required()
def book_appointment():
    data = request.get_json()
    patient_id = get_jwt_identity()

    if not data.get('doctor_id') or not data.get('date'):
        return jsonify({"error": "doctor_id and date required"}), 400

    # Validate doctor exists
    if not Doctor.query.get(data['doctor_id']):
        return jsonify({"error": "Doctor not found"}), 404

    try:
        appt_date = datetime.strptime(data['date'], '%Y-%m-%d %H:%M')
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD HH:MM"}), 400

    appt = Appointment(
        patient_id=patient_id,
        doctor_id=data['doctor_id'],
        date=appt_date,
        reason=data.get('reason', ''),
        status='Approved'
    )
    db.session.add(appt)
    db.session.commit()

    # USE to_dict() → NO parse error
    return jsonify({
        "message": "Appointment booked",
        "appointment": appt.to_dict()
    }), 201


# VIEW APPOINTMENTS
@appointment_bp.route('/appointments', methods=['GET'])
@jwt_required()
def get_appointments():
    patient_id = get_jwt_identity()
    appts = Appointment.query.filter_by(patient_id=patient_id).all()
    return jsonify({
        "appointments": [a.to_dict() for a in appts]
    }), 200


# CANCEL APPOINTMENT
@appointment_bp.route('/appointments/<int:id>', methods=['DELETE'])
@jwt_required()
def cancel_appointment(id):
    patient_id = get_jwt_identity()
    appt = Appointment.query.filter_by(id=id, patient_id=patient_id).first()

    if not appt:
        return jsonify({"error": "Appointment not found"}), 404

    db.session.delete(appt)
    db.session.commit()
    return jsonify({"message": "Appointment canceled"}), 200