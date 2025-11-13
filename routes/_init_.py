from .patients import patient_bp
from .doctors import doctor_bp
from .appointments import appointment_bp
from .prescriptions import prescription_bp

__all__ = [
    "patient_bp",
    "doctor_bp",
    "appointment_bp",
    "prescription_bp"
]
