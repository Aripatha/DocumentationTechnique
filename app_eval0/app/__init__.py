from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Initialisation de SQLAlchemy et LoginManager
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    
    # Configuration de l'application
    app.config.from_object('config.Config')
    
    # Initialiser les extensions avec l'application
    db.init_app(app)
    login_manager.init_app(app)
    
    # Importer les modèles après l'initialisation de db
    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Importer les routes (blueprints)
    from .views import main   # Utiliser .views pour l'import relatif
    app.register_blueprint(main)
    
    return app