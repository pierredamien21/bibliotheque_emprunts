# API - scaffold

Ce dossier contient un scaffold minimal pour une API FastAPI qui interagit
avec la base de données PostgreSQL. Il sert de point de départ : modèles,
schémas, routeurs et utilitaires de connexion DB.

Points importants :
- Configurez la variable d'environnement `DATABASE_URL` avant de lancer
  l'application (ex : `postgresql://postgres:postgres123@127.0.0.1:5433/postgres`).
- Installer les dépendances : `pip install -r requirements.txt`.
- Lancer localement : `uvicorn api.main:app --reload --host 127.0.0.1 --port 8000`.
