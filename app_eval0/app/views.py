import os
import json
import re
import sqlite3
import pickle
from flask import request, flash, redirect, url_for, render_template,Blueprint, session, current_app,jsonify
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User, Exam, Result
from app import db, mail
from flask_login import current_user, login_user, login_required, logout_user
from datetime import datetime, timedelta
import openai
from flask_mail import Message
from dotenv import load_dotenv

load_dotenv()
main = Blueprint('main', __name__)

# Configuration de l'API OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

ALLOWED_EXTENSIONS = {'pdf', 'docx'}

# Fonction pour se connecter à la base de données
def get_db_connection():
    db_path = "C:/Users/USER/Documents/GitHub/DocumentationTechnique/app_eval0/instance/users.db"
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main.route('/')
def index():
    return render_template('login.html')

@main.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    statut = request.form['statut']

    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password) and user.statut == statut:
        login_user(user)
        flash('Connexion réussie!', 'success')
        return redirect(url_for('main.dashboard'))
    flash('Échec de la connexion. Vérifiez vos identifiants.', 'error')
    return redirect(url_for('main.index'))

@main.route('/logout')
def logout():
    logout_user()
    flash('Vous avez été déconnecté.', 'info')
    return redirect(url_for('main.index'))

@main.route('/dashboard')
@login_required
def dashboard():
    if current_user.statut == 'enseignant':
        return render_template('teacher_dashboard.html', username=current_user.username)
    else:
        return redirect(url_for('main.student_dashboard'))


@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form.get('email')

        if not email:
            flash('L\'email est requis.', 'error')
            return redirect(url_for('main.register'))

        # Créer un nouvel utilisateur avec l'email fourni
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password, statut='enseignant', email=email)
        
        db.session.add(new_user)
        db.session.commit()
        flash('Inscription réussie! Vous pouvez maintenant vous connecter.', 'success')
        return redirect(url_for('main.index'))
    
    return render_template('register.html')

@main.route('/upload_exam', methods=['GET', 'POST'])
@login_required
def upload_exam():
    if request.method == 'POST' and current_user.statut == 'enseignant':
        file = request.files['fichier_examen']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join('uploads/', filename))

            doc_text = extract_text_from_file(os.path.join('uploads/', filename))
            questions = generate_exam_questions(doc_text)

            if questions:
                generate_exam_form(questions, current_user)
                flash('Examen généré et accessible aux étudiants!', 'success')
            else:
                flash('Échec de la génération de l’examen.', 'error')

            return redirect(url_for('main.dashboard'))
    
    #return render_template('upload_exam.html')

def extract_text_from_file(file_path):
    if file_path.endswith('.docx'):
        return extract_text_docx(file_path)
    elif file_path.endswith('.pdf'):
        return extract_text_pdf(file_path)

def extract_text_docx(file_path):
    from docx import Document
    doc = Document(file_path)
    return ' '.join([para.text for para in doc.paragraphs if para.text])

def extract_text_pdf(file_path):
    import PyPDF2
    text = []
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text.append(page.extract_text())
    return ' '.join(text)



def generate_exam_questions(doc_text):
    prompt = (
        f"Génère des questions d'examen à partir du texte suivant :\n\n{doc_text}\n\n"
        "Fournis un format JSON strictement valide avec des questions, leurs options pour les QCM (si applicable), "
        "le type ('qcm' ou 'qro'), et la réponse correcte pour les QCM."
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        generated_text = response.choices[0].message['content']
        print(f"Texte généré : {generated_text}")  # Debug

        # Nettoyage de texte JSON avec regex
        generated_text = re.sub(r",\s*}", "}", generated_text)  # Supprime les virgules avant les accolades fermantes
        generated_text = re.sub(r",\s*]", "]", generated_text)  # Supprime les virgules avant les crochets fermants

        # Suppression des doublons dans les options
        try:
            questions = json.loads(generated_text)
            for question in questions.get("questions", []):
                if question.get("type") == "qcm":
                    question["options"] = list(set(question["options"]))  # Supprime les doublons dans les options
            return questions
        except json.JSONDecodeError as e:
            print(f"Erreur de décodage JSON : {e}")
            return []

    except Exception as e:
        print(f"Erreur lors de la génération des questions : {e}")
        return []


# def generate_exam_questions(doc_text):
#     prompt = (
#         f"Génère des questions d'examen à partir du texte suivant :\n\n{doc_text}\n\n"
#         "Fournis un format JSON avec des questions, leurs options pour les QCM (si applicable), "
#         "le type ('qcm' ou 'qro'), et la réponse correcte pour les QCM."
#     )

#     try:
#         response = openai.ChatCompletion.create(
#             model="gpt-3.5-turbo",
#             messages=[{"role": "user", "content": prompt}]
#         )
#         generated_text = response.choices[0].message['content']
#         print(f"Texte généré : {generated_text}")  # Debug

#         # Vérifier si le texte généré est un JSON valide
#         try:
#             questions = json.loads(generated_text)
#             return questions
#         except json.JSONDecodeError as e:
#             print(f"Erreur de décodage JSON : {e}")
#             return []
#     except Exception as e:
#         print(f"Erreur lors de la génération des questions : {e}")
#         return []



# def generate_exam_questions(doc_text):
#     prompt = (
#         f"Génère des questions d'examen à partir du texte suivant :\n\n{doc_text}\n\n"
#         "Fournis un format JSON avec des questions, leurs options pour les QCM (si applicable), "
#         "le type ('qcm' ou 'qro'), et la réponse correcte pour les QCM."
#     )

#     try:
#         response = openai.ChatCompletion.create(
#             model="gpt-3.5-turbo",
#             messages=[{"role": "user", "content": prompt}]
#         )
#         generated_text = response.choices[0]['message']['content']
#         questions = json.loads(generated_text)
#         return questions
#     except Exception as e:
#         print(f"Erreur lors de la génération des questions : {e}")
#         return []

def generate_exam_form(questions, professor):
    new_exam = Exam(questions=questions, available_from=datetime.now(), duration=60, created_by=professor.id)
    db.session.add(new_exam)
    db.session.commit()

@main.route('/student_dashboard')
@login_required
def student_dashboard():
    current_time = datetime.now()
    available_exams = Exam.query.filter(Exam.available_from <= current_time).all()
    return render_template('student_dashboard.html', exams=available_exams)

# @main.route('/start_exam/<int:exam_id>', methods=['GET', 'POST'])
# @login_required
# def start_exam(exam_id):
#     exam = Exam.query.get_or_404(exam_id)

#     current_time = datetime.now()
#     if current_time < exam.available_from:
#         flash("Cet examen n'est pas encore disponible.", 'warning')
#         return redirect(url_for('main.student_dashboard'))

#     return render_template('exam_form.html', exam=exam, enumerate=enumerate)



#A effacer apres plusieurs tests 

@main.route('/start_exam/<int:exam_id>', methods=['GET'])
@login_required
def start_exam(exam_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM Exam WHERE id = ?", (exam_id,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        try:
            exam_data = {
                'id': result['id'],
                'available_from': result['available_from'],
                'duration': result['duration'],
                'created_by': result['created_by']
            }
            
            # Désérialiser les questions
            raw_questions = pickle.loads(result['questions'])
            
            # S'assurer que nous avons une liste de questions
            if isinstance(raw_questions, dict) and 'questions' in raw_questions:
                questions = raw_questions['questions']
            else:
                questions = raw_questions
                
            # Convertir en liste si ce n'est pas déjà le cas
            if not isinstance(questions, list):
                questions = [questions]
            
            # Nettoyer et valider chaque question
            formatted_questions = []
            for q in questions:
                if isinstance(q, dict):
                    formatted_question = {
                        'question': q.get('question', ''),
                        'type': q.get('type', 'qro'),
                        'options': q.get('options', []),
                        'reponse': q.get('reponse', '')
                    }
                    formatted_questions.append(formatted_question)
            
            print("Formatted Questions:", formatted_questions)  # Pour déboguer
            
            return render_template('exam_form.html', 
                                exam=exam_data, 
                                questions=formatted_questions)
                                
        except Exception as e:
            print(f"Error processing exam data: {str(e)}")
            flash("Erreur lors du chargement de l'examen.", 'error')
            return redirect(url_for('main.student_dashboard'))
    else:
        flash("Examen introuvable.", 'warning')
        return redirect(url_for('main.student_dashboard'))

# @main.route('/start_exam/<int:exam_id>', methods=['GET'])
# @login_required
# def start_exam(exam_id):
#     conn = get_db_connection()
#     cursor = conn.cursor()

#     # Retrieve the exam from the database by its ID
#     cursor.execute("SELECT * FROM Exam WHERE id = ?", (exam_id,))
#     result = cursor.fetchone()
#     conn.close()

#     if result:
#         # Assuming that 'result' contains the exam data and 'questions' is pickled in it
#         exam_data = {
#             'id': result['id'],
#             'available_from': result['available_from'],
#             'duration': result['duration'],
#             'created_by': result['created_by']
#         }
#         questions = pickle.loads(result['questions'])  # Deserialize the questions

#         # Pass both 'exam' and 'questions' to the template
#         return render_template('exam_form.html', exam=exam_data, questions=questions)
#     else:
#         flash("Examen introuvable.", 'warning')
#         return redirect(url_for('main.student_dashboard'))









# A effacer des que le code sera correcte 





# @main.route('/start_exam/<int:exam_id>', methods=['GET', 'POST'])
# @login_required
# def start_exam(exam_id):
#     conn = get_db_connection()
#     cursor = conn.cursor()
    
#     # Récupère l'examen en fonction de son ID
#     cursor.execute("SELECT questions FROM Exam WHERE id = ?", (exam_id,))
#     result = cursor.fetchone()
#     conn.close()

#     if result:
#         # Désérialise les questions
#         questions = pickle.loads(result['questions'])
#     else:
#         questions = []

#     return render_template('exam_form.html', questions=questions)
#     # exam = Exam.query.get_or_404(exam_id)

#     # # current_time = datetime.now()
#     # # if current_time < exam.available_from:
#     # #     flash("Cet examen n'est pas encore disponible.", 'warning')
#     # #     return redirect(url_for('main.student_dashboard'))

#     # # # Vérifiez si 'exam.questions' est déjà un dictionnaire
#     # # if isinstance(exam.questions, str):
#     # #     questions = json.loads(exam.questions)
#     # # else:
#     # #     questions = exam.questions

#     # # return render_template('exam_form.html', exam=exam, questions=questions, enumerate=enumerate)
#     # # Pas besoin de décodage JSON, accédez directement aux questions
#     # questions = exam.questions  # Puisque 'questions' est déjà une liste de dictionnaires
    
#     # # Renvoyer les données à 'exam_form.html'
#     # # return render_template('exam_form.html', exam=exam, questions=questions)
#     # questions = exam.questions  # Puisque 'questions' est déjà une liste de dictionnaires
#     # print(type(questions))
#     # print(questions)  # Pour vérifier toutes les questions

#     # # Vérification des données
#     # if not isinstance(questions, list) or not questions:
#     #     questions = [{"question": "Aucune question trouvée pour cet examen.", "type": "message"}]

#     # return render_template('exam_form.html', exam=exam, questions=questions)
    
# @main.route('/start_exam/<int:exam_id>', methods=['GET'])
# @login_required
# def start_exam(exam_id):
#     conn = get_db_connection()
#     cursor = conn.cursor()
    
#     # Récupère l'examen en fonction de son ID
#     cursor.execute("SELECT questions FROM Exam WHERE id = ?", (exam_id,))
#     result = cursor.fetchone()
#     conn.close()

#     if result:
#         # Désérialise les questions
#         questions = pickle.loads(result['questions'])
#         print("Questions désérialisées:", questions)  # Affiche les questions récupérées pour vérifier leur contenu
#     else:
#         questions = []

#     return render_template('exam_form.html', questions=questions)

#test debug code formulaire 


# @main.route('/start_exam/<int:exam_id>', methods=['GET', 'POST'])
# @login_required
# def start_exam(exam_id):
#     exam = Exam.query.get_or_404(exam_id)

#     current_time = datetime.now()
#     if current_time < exam.available_from:
#         flash("Cet examen n'est pas encore disponible.", 'warning')
#         return redirect(url_for('main.student_dashboard'))

#     # Désérialiser les questions
#     questions = json.loads(exam.questions)

#     return render_template('exam_form.html', exam=exam, questions=questions, enumerate=enumerate)

@main.route('/submit_exam', methods=['POST'])
@login_required
def submit_exam():
    exam_id = request.form.get('exam_id')
    exam = Exam.query.get(exam_id)

    student_answers = []
    for index, question in enumerate(exam.questions):
        answer = request.form.get(f'answers_{index}')
        student_answers.append(answer)

    score = correct_exam(student_answers, exam.questions)
    save_result(current_user.username, score, exam_id)
    send_result_to_professor(current_user.username, score, exam_id, exam.created_by)

    flash(f'Votre score est de {score} sur {len(exam.questions)}.', 'info')
    return redirect(url_for('main.student_dashboard'))

# def correct_exam(student_answers, questions):
#     score = 0
#     for answer, question in zip(student_answers, questions):
#         # Convertir la question en dictionnaire si c'est une chaîne de caractères
#         if isinstance(question, str):
#             question = json.loads(question)
        
#         if question.get('type') == 'qcm' and answer == question.get('correct_answer'):
#             score += 1
#         elif question.get('type') == 'qro':
#             score += correct_qro_with_openai(answer, question['question'])
#     return score
def correct_exam(student_answers, questions):
    score = 0
    for answer, question in zip(student_answers, questions):
        # Vérifiez si la question est une chaîne de caractères et n'est pas vide
        if isinstance(question, str) and question.strip():
            try:
                print(f"Question avant décodage : {question}")

                question = json.loads(question)
            except json.JSONDecodeError:
                print(f"Erreur de décodage JSON : {question}")
                continue  # Ignore cette question et passe à la suivante
        
        if question.get('type') == 'qcm' and answer == question.get('correct_answer'):
            score += 1
        elif question.get('type') == 'qro':
            score += correct_qro_with_openai(answer, question['question'])
    return score

def correct_qro_with_openai(student_answer, question):
    prompt = (
        f"Corrige cette réponse étudiante pour la question suivante :\n\n"
        f"Question : {question}\nRéponse étudiante : {student_answer}\n\n"
        "Attribue une note de 0 à 1 selon la pertinence de la réponse."
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        score = float(response.choices[0]['message']['content'])
        return score
    except Exception as e:
        print(f"Erreur lors de la correction avec OpenAI : {e}")
        return 0
# def generate_exam_questions(doc_text):
#     prompt = (
#         f"Génère des questions d'examen à partir du texte suivant :\n\n{doc_text}\n\n"
#         "Fournis un format JSON avec des questions, leurs options pour les QCM (si applicable), "
#         "le type ('qcm' ou 'qro'), et la réponse correcte pour les QCM."
#     )

#     try:
#         response = openai.ChatCompletion.create(
#             model="gpt-3.5-turbo",
#             messages=[{"role": "user", "content": prompt}]
#         )
#         generated_text = response.choices[0].message['content']
#         questions = json.loads(generated_text)
#         return questions
#     except Exception as e:
#         print(f"Erreur lors de la génération des questions : {e}")
#         return []

# def generate_exam_form(questions, professor):
#     new_exam = Exam(questions=questions, available_from=datetime.now(), duration=60, created_by=professor.id)
#     db.session.add(new_exam)
#     db.session.commit()

# @main.route('/student_dashboard')
# @login_required
# def student_dashboard():
#     current_time = datetime.now()
#     available_exams = Exam.query.filter(Exam.available_from <= current_time).all()
#     return render_template('student_dashboard.html', exams=available_exams)

# @main.route('/start_exam/<int:exam_id>', methods=['GET', 'POST'])
# @login_required
# def start_exam(exam_id):
#     exam = Exam.query.get_or_404(exam_id)

#     current_time = datetime.now()
#     if current_time < exam.available_from:
#         flash("Cet examen n'est pas encore disponible.", 'warning')
#         return redirect(url_for('main.student_dashboard'))

#     return render_template('exam_form.html', exam=exam)

# @main.route('/submit_exam', methods=['POST'])
# @login_required
# def submit_exam():
#     exam_id = request.form.get('exam_id')
#     exam = Exam.query.get(exam_id)

#     student_answers = []
#     for index, question in enumerate(exam.questions):
#         answer = request.form.get(f'answers_{index}')
#         student_answers.append(answer)

#     score = correct_exam(student_answers, exam.questions)
#     save_result(current_user.username, score, exam_id)
#     send_result_to_professor(current_user.username, score, exam_id, exam.created_by)

#     flash(f'Votre score est de {score} sur {len(exam.questions)}.', 'info')
#     return redirect(url_for('main.student_dashboard'))

# def correct_exam(student_answers, questions):
#     score = 0
#     for answer, question in zip(student_answers, questions):
#         if question.get('type') == 'qcm' and answer == question.get('correct_answer'):
#             score += 1
#         elif question.get('type') == 'qro':
#             score += correct_qro_with_openai(answer, question['question'])
#     return score

# def correct_qro_with_openai(student_answer, question):
#     prompt = (
#         f"Corrige cette réponse étudiante pour la question suivante :\n\n"
#         f"Question : {question}\nRéponse étudiante : {student_answer}\n\n"
#         "Attribue une note de 0 à 1 selon la pertinence de la réponse."
#     )

#     try:
#         response = openai.ChatCompletion.create(
#             model="gpt-3.5-turbo",
#             messages=[{"role": "user", "content": prompt}]
#         )
#         score = float(response.choices[0].message['content'])
#         return score
#     except Exception as e:
#         print(f"Erreur lors de la correction avec OpenAI : {e}")
#         return 0

def save_result(username, score, exam_id):
    result = Result(username=username, score=score, exam_id=exam_id)
    db.session.add(result)
    db.session.commit()

import smtplib
def send_result_to_professor(username, score, exam_id, professor_id):
    professor = User.query.get(professor_id)
    if professor:
        msg = Message(
            'Résultat d\'examen',
            sender='expediteur@exemple.com',  # Assurez-vous de remplacer par un expéditeur valide
            recipients=[professor.email]
        )
        msg.body = f"Étudiant: {username}, Score: {score}, Examen ID: {exam_id}"
        try:
            mail.send(msg)
            print("E-mail envoyé avec succès")
        except smtplib.SMTPException as e:
            print(f"Erreur lors de l'envoi de l'e-mail: {e}")
        except Exception as e:
            print(f"Une autre erreur est survenue: {e}")


@main.route('/add_student', methods=['GET', 'POST'])
@login_required
def add_student():
    if request.method == 'POST' and current_user.statut == 'enseignant':
        username = request.form['username']
        password = request.form['password']
        email = request.form.get('email')

        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            flash("L'étudiant existe déjà.", 'error')
            return redirect(url_for('main.dashboard'))

        new_student = User(username=username, password=generate_password_hash(password), statut='étudiant',email=email)
        db.session.add(new_student)
        db.session.commit()

        flash("L'étudiant a été ajouté avec succès.", 'success')
        return redirect(url_for('main.dashboard'))

    return render_template('add_student.html')

@main.route('/report_event', methods=['POST'])
def report_event():
    data = request.get_json()
    alert_message = data.get('alert')
    # Log ou gestion de l'alerte ici
    print(f"Alerte de sécurité reçue: {alert_message}")
    return jsonify({"status": "success"}), 200

def test_send_email():
    msg = Message("Test Email", 
                  sender=os.getenv('MAIL_DEFAULT_SENDER'),
                  recipients=["bnjabnja04@gmail.com"])
    msg.body = "Ceci est un email de test."
    try:
        mail.send(msg)
        print("Email envoyé avec succès !")
    except Exception as e:
        print("Erreur lors de l'envoi de l'email:", e)