# routes/prescriptions.py
from flask import Blueprint, request, jsonify
from extensions import db
from models.prescriptions import Prescription
from models.doctors import Doctor
from models.patients import Patient
from models.appointments import Appointment
from flask_jwt_extended import jwt_required, get_jwt_identity

prescription_bp = Blueprint('prescriptions', __name__)

# CREATE PRESCRIPTION (Doctor only)
@prescription_bp.route('/prescriptions', methods=['POST'])
@jwt_required()
def create_prescription():
    doctor_id = get_jwt_identity()
    data = request.get_json()

    # Validate doctor
    if not Doctor.query.get(doctor_id):
        return jsonify({"error": "Doctor not found"}), 404

    required = ['patient_id', 'drug_name', 'dosage']
    for field in required:
        if field not in data or not data[field]:
            return jsonify({"error": f"'{field}' required"}), 400

    # Validate patient
    if not Patient.query.get(data['patient_id']):
        return jsonify({"error": "Patient not found"}), 404

    # Optional: Validate appointment
    if data.get('appointment_id'):
        appt = Appointment.query.get(data['appointment_id'])
        if not appt or appt.doctor_id != doctor_id:
            return jsonify({"error": "Invalid appointment"}), 400

    prescription = Prescription(
        doctor_id=doctor_id,
        patient_id=data['patient_id'],
        appointment_id=data.get('appointment_id'),
        drug_name=data['drug_name'],
        dosage=data['dosage'],
        instructions=data.get('instructions', '')
    )
    db.session.add(prescription)
    db.session.commit()

    # USE to_dict() → NO parse error
    return jsonify({
        "message": "Prescription created",
        "prescription": prescription.to_dict()
    }), 201


# GET PRESCRIPTIONS (Doctor or Patient)
@prescription_bp.route('/prescriptions', methods=['GET'])
@jwt_required()
def get_prescriptions():
    user_id = get_jwt_identity()
    doctor = Doctor.query.get(user_id)
    patient = Patient.query.get(user_id)

    if doctor:
        prescriptions = Prescription.query.filter_by(doctor_id=user_id).all()
    elif patient:
        prescriptions = Prescription.query.filter_by(patient_id=user_id).all()
    else:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "prescriptions": [p.to_dict() for p in prescriptions]
    }), 200


# DELETE PRESCRIPTION (Doctor only)
@prescription_bp.route('/prescriptions/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_prescription(id):
    doctor_id = get_jwt_identity()
    prescription = Prescription.query.filter_by(id=id, doctor_id=doctor_id).first()

    if not prescription:
        return jsonify({"error": "Not found or unauthorized"}), 404

    db.session.delete(prescription)
    db.session.commit()
    return jsonify({"message": "Prescription deleted"}), 200