# API Bibliothèque : gestion des emprunts

API REST qui gère le fonctionnement d'une bibliothèque : catalogue, exemplaires, membres, emprunts, réservations et sanctions. L'interface web associée est dans [frontend_biblio_emprunts](https://github.com/pierredamien21/frontend_biblio_emprunts).

## Fonctionnalités

- **Deux types de comptes** : les membres et les bibliothécaires, avec une connexion unifiée par jeton JWT et des mots de passe hachés (bcrypt).
- **Catalogue** : livres, auteurs, catégories, exemplaires physiques, et téléversement des couvertures.
- **Cycle de prêt** : emprunt, retour et réservation. Chaque type de membre fixe sa durée maximale et son nombre maximal d'emprunts. Les sanctions (amende ou suspension) sont enregistrées par membre.
- **Vie du compte** : avis, favoris, messages et notifications.
- **Statistiques** pour les bibliothécaires.
- **Base PostgreSQL** : modèles SQLAlchemy, migrations Alembic et scripts SQL (tables, index, triggers, vues, permissions) dans `tables_index_tiggers/`.

L'API compte 73 routes réparties en 18 groupes (`/livres`, `/emprunts`, `/reservations`, `/sanctions`, `/stats`…), toutes documentées sur `/docs`.

## Structure

```
api/
├── main.py         application FastAPI
├── routers/        une route par ressource
├── models/         modèles SQLAlchemy
├── schemas/        schémas Pydantic
├── migrations/     migrations Alembic
├── security.py     JWT et hachage
└── tests/          tests pytest et scripts de vérification
tables_index_tiggers/   SQL de la base
render.yaml             déploiement sur Render
```

## Installation

Prérequis : Python 3.11 et une base PostgreSQL (locale ou Supabase).

```bash
python -m venv .venv && source .venv/bin/activate   # Windows : .venv\Scripts\activate
pip install -r requirements.txt
export DATABASE_URL="postgresql://utilisateur:motdepasse@localhost:5432/bibliotheque"
export SECRET_KEY="une_cle_longue_et_aleatoire"
export ADMIN_PASSWORD="mot_de_passe_du_premier_admin"
python api/init_db.py && python api/seed_types.py && python api/seed_admin.py
uvicorn api.main:app --reload
```

Toutes les variables sont décrites dans `ENV_CONFIG.md`. La documentation interactive est sur http://127.0.0.1:8000/docs.

## Tests

```bash
pytest api/tests
```

Les tests pytest tournent sur une base SQLite en mémoire. Ils couvrent les opérations de base, l'authentification des membres, le refus des accès non autorisés, le téléversement et le parcours complet d'un emprunt. Les scripts `local_*_check.py` et `live_api_check.py` vérifient une API déjà lancée.

## Documentation

- `DOCUMENTATION_API.md` : référence des routes.
- `NOTICE_UTILISATEUR.md` : guide d'utilisation par rôle.
- `ENV_CONFIG.md` : configuration et déploiement.

## Stack

Python · FastAPI · SQLAlchemy · Alembic · PostgreSQL · Pydantic · JWT · bcrypt · pytest · Render
