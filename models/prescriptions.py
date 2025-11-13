# models/prescriptions.py
from extensions import db

class Prescription(db.Model):
    __tablename__ = 'prescriptions'

    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'), nullable=True)  # ← Optional
    drug_name = db.Column(db.String(200), nullable=False)
    dosage = db.Column(db.String(100), nullable=False)
    instructions = db.Column(db.String(500), nullable=True)

    # Relationships (optional)
    doctor = db.relationship('Doctor', backref='prescriptions')
    patient = db.relationship('Patient', backref='prescriptions')
    appointment = db.relationship('Appointment', backref='prescriptions')

    def to_dict(self):
        return {
            'id': self.id,
            'doctor_id': self.doctor_id,
            'patient_id': self.patient_id,
            'appointment_id': self.appointment_id,
            'drug_name': self.drug_name,
            'dosage': self.dosage,
            'instructions': self.instructions,
            'doctor_full_name': self.doctor.full_name if self.doctor else "Unknown"
        }