import sqlite3

# Chemin vers votre fichier .db  a modifier  selon ou est stocker le projet dans votre ordinateur 
db_path = "C:/Users/USER/Documents/GitHub/DocumentationTechnique/app_eval0/instance/users.db"


# Connexion à la base de données SQLite
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Requête pour vérifier le statut d'un utilisateur
username = "kaemly000@gmail.com"
cursor.execute("SELECT username, statut FROM User WHERE username = ?", (username,))
result = cursor.fetchone()

if result:
    print(f"Utilisateur: {result[0]}, Statut: {result[1]}")
else:
    print("Utilisateur non trouvé.")

# Fermer la connexion
conn.close()
