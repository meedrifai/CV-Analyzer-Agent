✅ TODO LIST FINALISATION — CV Classifier
1. 🐳 Conteneurisation avec Docker
Objectif : Dockeriser tout le backend (FastAPI ou Flask), prêt à être exécuté partout.

📁 Fichiers à créer :
Dockerfile :

dockerfile
Copier
Modifier
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "run:app", "--host", "0.0.0.0", "--port", "8000"]
.dockerignore :

bash
Copier
Modifier
__pycache__/
*.pyc
.env
requirements.txt (généré avec pip freeze > requirements.txt)

▶️ Commandes :
bash
Copier
Modifier
# Build
docker build -t cv-classifier .

# Run
docker run -d -p 8000:8000 cv-classifier
2. 🚀 Déploiement en ligne (Gratuit)
✅ Meilleure option gratuite :
👉 Render — gratuit, simple à utiliser, bon pour FastAPI.

⚙️ Étapes :
Pousse ton projet sur GitHub.

Va sur Render > New > Web Service

Connecte ton repo.

Paramètres :

Build command: pip install -r requirements.txt

Start command: uvicorn run:app --host 0.0.0.0 --port 10000

Python environment: 3.12

Ajoute les variables d’environnement .env dans Render.

Clic sur Deploy.

Résultat : une URL publique ex : https://cv-classifier.onrender.com

3. 📊 Dashboard des CV reçus
Objectif : voir tous les CV reçus, avec les prédictions + métadonnées du formulaire.

💡 Choix technique :
Interface : ReactJS ou simple HTML + Bootstrap

Backend : ajoute un endpoint /dashboard qui retourne les données

Base de données : SQLite ou PostgreSQL (Render supporte les deux)

🗃️ Données à stocker :
Nom	Email	URL du CV	Prédiction	Date réception

✅ Exemple d’approche simple :
Lors du POST webhook, enregistre :

python
Copier
Modifier
from datetime import datetime

cv_log = {
    "nom": responses["Nom"],
    "email": responses["Email"],
    "cv_url": save_cv_to_drive_or_s3(),  # lien vers le fichier
    "prediction": predicted_label,
    "date": datetime.now().isoformat()
}
collection.insert_one(cv_log)
Crée un route /dashboard qui :

Authentifie l'utilisateur (token simple)

Renvoie les CV dans une page HTML, tableau Bootstrap, trié par date.

➕ BONUS (optionnel)
🔐 Auth simple avec token pour protéger /dashboard

📥 Export CSV des données reçues

📈 Ajouter des stats : combien de CV / jour / catégories