from extensions import db, bcrypt

class Patient(db.Model):
    """
    Represents a patient in the clinic system.
    Patients can register, log in, and book appointments.
    """
    __tablename__ = 'patients'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    address = db.Column(db.String(200), nullable=True)

    def __init__(self, full_name: str, email: str, password: str, phone: str, address: str = None):
        """
        Initialize a new Patient instance with hashed password.
        """
        self.full_name = full_name
        self.email = email
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')
        self.phone = phone
        self.address = address

    def check_password(self, password: str) -> bool:
        """
        Verify a plaintext password against the stored hash.
        """
        return bcrypt.check_password_hash(self.password, password)

    def to_dict(self) -> dict:
        """
        Return a dictionary representation (excluding password).
        Useful for safe API responses.
        """
        return {
            'id': self.id,
            'full_name': self.full_name,
            'email': self.email,
            'phone': self.phone,
            'address': self.address
        }

    def __repr__(self):
        return f"<Patient {self.full_name}>"
