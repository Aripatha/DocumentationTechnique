from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')  # Chargement de la configuration
    db.init_app(app)  # Initialisation de SQLAlchemy

    from app.views import main
    app.register_blueprint(main)  # Enregistrement des routes

    return app