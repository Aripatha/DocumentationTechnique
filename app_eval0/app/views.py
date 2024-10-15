from flask import Blueprint, render_template, request, redirect, url_for, flash, session,current_app
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models import User
from flask_login import current_user, login_user
from flask_migrate import Migrate

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('login.html')

@main.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    statut = request.form['statut']

    # Vérification de l'utilisateur
    user = User.query.filter_by(username=username).first()
    
    # if user and check_password_hash(user.password, password) and user.statut == statut:
    #     login_user(user)  # Authentifie l'utilisateur
    #     flash('Connexion réussie !', 'success')
    #     return redirect(url_for('main.dashboard'))  # Redirige vers le tableau de bord
    # else:
    #     flash('Échec de la connexion. Vérifiez vos identifiants.', 'error')
    #     return redirect(url_for('main.index'))

    #a effacer apres les tests 
    if user:
        print(f"Statut de l'utilisateur récupéré : {user.statut}")
    if check_password_hash(user.password, password) and user.statut == statut:
        login_user(user)
        flash('Connexion réussie !', 'success')
        return redirect(url_for('main.dashboard'))
    flash('Échec de la connexion. Vérifiez vos identifiants.', 'error')
    return redirect(url_for('main.index'))


@main.route('/dashboard')
def dashboard():
    if current_user.is_authenticated:
        if current_user.statut == 'enseignant':
            return render_template('teacher_dashboard.html', username=current_user.username)
        else:
            return f"Bienvenue, {current_user.username} ! Vous êtes connecté en tant qu'étudiant."
    return redirect(url_for('main.index'))

@main.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('statut', None)
    flash('Vous avez été déconnecté.', 'info')
    return redirect(url_for('main.index'))

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        statut ='enseignant'  # definit par defaut 

        # Hacher le mot de passe
        hashed_password = generate_password_hash(password)

        # Créer un nouvel utilisateur
        new_user = User(username=username, password=hashed_password, statut=statut)
        db.session.add(new_user)
        db.session.commit()
        flash('Inscription réussie ! Vous pouvez vous connecter.', 'success')
        return redirect(url_for('main.index'))

    return render_template('register.html')

# Décorateur pour vérifier que l'utilisateur est un enseignant
def teacher_required(f):
    def wrapper(*args, **kwargs):
        if current_user.statut != 'enseignant':
            return "Accès interdit", 403  # Code 403 : accès refusé
        return f(*args, **kwargs)
    return wrapper

# Route pour ajouter un étudiant
@main.route('/add_student', methods=['GET', 'POST'])
@teacher_required
def add_student():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("L'étudiant existe déjà.", 'error')
            return redirect(url_for('main.index'))
        
        new_student = User(
            username=username,
            password=generate_password_hash(password),
            statut='étudiant'  # Utiliser 'statut'
        )

        #a effacer apres les tests 
        print(f"Statut attribué à l'utilisateur {username} : {new_student.statut}")

        db.session.add(new_student)
        db.session.commit()
        
        
        flash("L'étudiant a été ajouté avec succès.", 'success')
        return redirect(url_for('main.index'))
        
    
    return render_template('add_student.html')
@main.route('/routes')
def routes():
    output = []
    for rule in current_app.url_map.iter_rules():
        output.append(str(rule))
    return '<br>'.join(output)