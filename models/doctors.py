from extensions import db, bcrypt

class Doctor(db.Model):
    __tablename__ = 'doctors'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    specialty = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    is_available = db.Column(db.Boolean, default=True)  # Doctor availability

    def __init__(self, full_name, email, password, specialty, phone):
        self.full_name = full_name
        self.email = email
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')
        self.specialty = specialty
        self.phone = phone

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

    def to_dict(self):
        return {
            'id': self.id,
            'full_name': self.full_name,
            'email': self.email,
            'specialty': self.specialty,
            'phone': self.phone,
            'is_available': self.is_available
        }

    def __repr__(self):
        return f"<Doctor {self.full_name}>"
