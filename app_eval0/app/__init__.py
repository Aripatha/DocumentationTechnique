from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
import os
from flask_migrate import Migrate

# Initialisation de SQLAlchemy et LoginManager
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()

def create_app():
    app = Flask(__name__)
    
    # Configuration de l'application
    app.config.from_object('config.Config')
    
    # Initialiser les extensions avec l'application
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    
   # Configuration de l'application
    app.config['UPLOAD_FOLDER'] = 'uploads/'

    # Créer le dossier 'uploads/' s'il n'existe pas
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    # Importer les modèles après l'initialisation de db
    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Importer les routes (blueprints)
    from .views import main   # Utiliser .views pour l'import relatif
    app.register_blueprint(main)
    
    return app
