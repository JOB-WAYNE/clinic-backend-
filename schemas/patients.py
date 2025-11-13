# schemas/patients.py
from extensions import ma
from marshmallow import fields, ValidationError

class PatientSchema(ma.Schema):
    id = fields.Int(dump_only=True)
    full_name = fields.Str(required=True)
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)
    phone = fields.Str(required=True)
    address = fields.Str(required=False, allow_none=True)

    @validates('password')
    def validate_password(self, value):
        if len(value) < 6:
            raise ValidationError("Password must be at least 6 characters")

# Instances
patient_schema = PatientSchema()
patients_schema = PatientSchema(many=True)