from app import create_app

app = create_app()

if __name__ == '__main__':
    print("Démarrage du serveur Flask...")
    app.run(debug=True)
    app.register_blueprint('__main__')
    print("Serveur démarré avec succès !")  # Cela ne sera pas exécuté tant que le serveur 