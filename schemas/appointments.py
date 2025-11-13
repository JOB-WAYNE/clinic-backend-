# schemas/appointments.py
from extensions import ma
from marshmallow import fields

class AppointmentSchema(ma.Schema):
    id = fields.Int(dump_only=True)
    patient_id = fields.Int(dump_only=True)  # ← Correct: set in code
    doctor_id = fields.Int(required=True)
    date = fields.Str(required=True)
    reason = fields.Str()
    status = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True, format="%Y-%m-%d %H:%M")
    doctor_name = fields.Method("get_doctor_name", dump_only=True)

    def get_doctor_name(self, obj):
        return obj.doctor.full_name if obj.doctor else "Unknown"