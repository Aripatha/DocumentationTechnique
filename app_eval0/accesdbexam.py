import sqlite3
import pickle

# Chemin vers le fichier .db - ajustez ce chemin en fonction de l'emplacement de votre fichier
db_path = "C:/Users/USER/Documents/GitHub/DocumentationTechnique/app_eval0/instance/users.db"

# Connexion à la base de données SQLite
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Requête pour récupérer les questions de l'examen avec id=11
cursor.execute("SELECT questions FROM Exam WHERE id=11")
result = cursor.fetchone()  # Utilisez `fetchone()` car un seul enregistrement est attendu

if result:
    # Données brutes sérialisées
    raw_data = result[0]
    print("Données brutes de l'examen:", raw_data)
    
    # Désérialisation des données avec pickle
    try:
        questions_data = pickle.loads(raw_data)
        print("Questions désérialisées avec Pickle:")
        
        # Parcourir et afficher chaque question
        for i, question in enumerate(questions_data["questions"], start=1):
            print(f"Question {i}:")
            print(f"  Texte : {question.get('question')}")
            print(f"  Type : {question.get('type')}")
            if question.get("type") == "qcm":
                print("  Options :")
                for option in question.get("options", []):
                    print(f"    - {option}")
                print(f"  Réponse correcte : {question.get('reponse')}")
            elif question.get("type") == "qro":
                print(f"  Réponse attendue : {question.get('reponse')}")
            print("\n")  # Ligne vide entre les questions pour la lisibilité

    except Exception as e:
        print("Erreur lors de la désérialisation avec Pickle:", e)
else:
    print("Aucun examen trouvé.")

# Fermer la connexion
conn.close()
