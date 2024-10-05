from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from .models import User
from . import db
from werkzeug.security import generate_password_hash, check_password_hash

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
    
    if user and check_password_hash(user.password, password) and user.statut == statut:
        session['username'] = username
        session['statut'] = statut  # Ajoute le statut à la session
        flash('Connexion réussie !', 'success')
        return redirect(url_for('main.dashboard'))  # Redirige vers le tableau de bord
    else:
        flash('Échec de la connexion. Vérifiez vos identifiants.', 'error')
        return redirect(url_for('main.index'))

@main.route('/dashboard')
def dashboard():
    if 'username' in session:
        if session['statut'] == 'enseignant':
            return render_template('teacher_dashboard.html', username=session['username'])
        else:
            return f"Bienvenue, {session['username']} ! Vous êtes connecté en tant qu'étudiant."
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
        statut = "enseignant"  # Statut est toujours "enseignant"

        # Hacher le mot de passe
        hashed_password = generate_password_hash(password)

        # Créer un nouvel utilisateur
        new_user = User(username=username, password=hashed_password, statut=statut)
        db.session.add(new_user)
        db.session.commit()
        flash('Inscription réussie ! Vous pouvez vous connecter.', 'success')
        return redirect(url_for('main.index'))

    return render_template('register.html')  # Crée un template register.html si nécessaire