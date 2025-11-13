# schemas/prescriptions.py
from extensions import ma
from marshmallow import fields, ValidationError
from sqlalchemy.orm import joinedload

class PrescriptionSchema(ma.Schema):
    id = fields.Int(dump_only=True)
    doctor_id = fields.Int(required=True)
    patient_id = fields.Int(required=True)
    appointment_id = fields.Int(required=False)
    drug_name = fields.Str(required=True)
    dosage = fields.Str(required=True)
    instructions = fields.Str(dump_default='', allow_none=False)
    doctor_name = fields.Method("get_doctor_name", dump_only=True)

    class Meta:
        ordered = True

    def get_doctor_name(self, obj):
        return obj.doctor.full_name if obj.doctor else "Unknown"

    @validates('drug_name')
    def validate_drug_name(self, value):
        if len(value) > 200:
            raise ValidationError("drug_name too long (max 200)")