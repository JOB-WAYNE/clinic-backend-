# models/appointments.py
from extensions import db
from datetime import datetime

class Appointment(db.Model):
    __tablename__ = 'appointments'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    reason = db.Column(db.String(250), nullable=True)
    status = db.Column(db.String(50), default=lambda: 'Approved')  # FIXED
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    patient = db.relationship('Patient', backref=db.backref('appointments', lazy=True))
    doctor = db.relationship('Doctor', backref=db.backref('appointments', lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "doctor_id": self.doctor_id,
            "doctor_name": self.doctor.full_name if self.doctor else "Unknown",
            "date": self.date.strftime("%Y-%m-%d %H:%M"),
            "reason": self.reason,
            "status": self.status,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M")
        }

    def __repr__(self):
        return f"<Appointment {self.id} - Patient {self.patient_id} with Doctor {self.doctor_id}>"