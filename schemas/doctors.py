# schemas/doctors.py
from extensions import ma

class DoctorSchema(ma.Schema):
    class Meta:
        fields = (
            'id',
            'full_name',
            'email',
            'specialty',
            'phone',
            'is_available'
        )

doctor_schema = DoctorSchema()
doctors_schema = DoctorSchema(many=True)