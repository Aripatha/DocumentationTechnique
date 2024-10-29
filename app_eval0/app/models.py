from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = 'User'  # Spécifier le nom de la table en majuscules

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    statut = db.Column(db.String(10), nullable=False)  # 'étudiant' ou 'enseignant'
    email = db.Column(db.String(120), unique=True, nullable=False)

    
    def set_password(self, password):
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password, password)

    # Propriétés requises par Flask-Login
    @property
    def is_active(self):
        return True  # L'utilisateur est actif

    @property
    def is_authenticated(self):
        return True  # L'utilisateur est authentifié

    @property
    def is_anonymous(self):
        return False  # L'utilisateur n'est pas anonyme
    

class Exam(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    questions = db.Column(db.PickleType)  # Liste de questions
    available_from = db.Column(db.DateTime)  # Date de disponibilité
    duration = db.Column(db.Integer)  # Durée en minutes
    created_by = db.Column(db.Integer, db.ForeignKey('User.id'))

class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    score = db.Column(db.Integer, nullable=True)
    exam_id = db.Column(db.Integer, db.ForeignKey('exam.id'), nullable=False)  