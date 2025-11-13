# app.py
import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_migrate import Migrate  # ← MIGRATIONS
from extensions import db, ma, bcrypt, jwt
from routes.patients import patient_bp
from routes.doctors import doctor_bp
from routes.prescriptions import prescription_bp

def create_app():
    app = Flask(__name__)
    CORS(app)

    # FULL ABSOLUTE PATH TO DATABASE
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DB_PATH = os.path.join(BASE_DIR, 'clinic.db')
    print(f"DB will be created at: {DB_PATH}")

    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'supersecretkey'

    # Initialize extensions
    db.init_app(app)
    ma.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)

    # MIGRATIONS
    Migrate(app, db)

    # Register blueprints
    app.register_blueprint(patient_bp)
    app.register_blueprint(doctor_bp)
    app.register_blueprint(prescription_bp)

    # REMOVED db.create_all() — MIGRATIONS WILL HANDLE IT
    # with app.app_context():
    #     db.create_all()

    @app.route('/')
    def home():
        return jsonify({
            "message": "Clinic API READY",
            "status": "Using Flask-Migrate",
            "db_path": DB_PATH
        })

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)