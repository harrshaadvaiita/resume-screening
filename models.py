from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    resume_filename = db.Column(db.String(255), nullable=False)
    score = db.Column(db.Float, nullable=True)

def get_all_candidates():
    return Candidate.query.all()