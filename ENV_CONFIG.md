# Guide de Configuration des Variables d'Environnement

## 📋 Configuration Initiale

1. **Copier le fichier exemple** :
   ```bash
   cp .env.example .env
   ```

2. **Éditer le fichier `.env`** avec vos valeurs réelles.

---

## 🔑 Variables Obligatoires

### `DATABASE_URL`
**Description** : Chaîne de connexion PostgreSQL pour Supabase ou base locale.

**Format** :
```
postgresql://user:password@host:port/database
```

**Exemples** :
- **Local** : `postgresql://postgres:postgres123@127.0.0.1:5433/postgres`
- **Supabase** : `postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres`

> [!IMPORTANT]
> Pour Supabase, récupérez l'URL dans : **Project Settings** → **Database** → **Connection String** (mode "URI")

---

### `SECRET_KEY`
**Description** : Clé secrète pour signer les tokens JWT.

**Génération sécurisée** :
```bash
openssl rand -hex 32
```

**Exemple** :
```
SECRET_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6
```

> [!CAUTION]
> **Ne JAMAIS** commiter cette clé dans Git. Elle doit être unique par environnement.

---

## ⚙️ Variables Optionnelles

### `ACCESS_TOKEN_EXPIRE_MINUTES`
**Description** : Durée de validité des tokens JWT (en minutes).

**Valeur par défaut** : `30`

**Recommandations** :
- **Développement** : `60` (1 heure)
- **Production** : `30` (30 minutes)

---

### `ENVIRONMENT`
**Description** : Environnement d'exécution.

**Valeurs possibles** : `development`, `staging`, `production`

**Utilisation** : Pour activer/désactiver des fonctionnalités selon l'environnement.

---

### `API_HOST` et `API_PORT`
**Description** : Configuration du serveur local.

**Valeurs par défaut** :
- `API_HOST=127.0.0.1`
- `API_PORT=8000`

---

## 🚀 Déploiement sur Render

Sur Render, configurez les variables d'environnement dans :
**Dashboard** → **Environment** → **Environment Variables**

Variables à définir :
1. `DATABASE_URL` : URL Supabase
2. `SECRET_KEY` : Généré automatiquement par Render ou manuellement

> [!NOTE]
> Le fichier `render.yaml` configure `SECRET_KEY` avec `generateValue: true` pour une génération automatique.

---

## ✅ Vérification

Pour vérifier que les variables sont bien chargées :

```python
# Dans un fichier Python
import os
from dotenv import load_dotenv

load_dotenv()

print(f"DATABASE_URL: {os.getenv('DATABASE_URL')[:20]}...")  # Affiche les 20 premiers caractères
print(f"SECRET_KEY définie: {bool(os.getenv('SECRET_KEY'))}")
print(f"Token expire après: {os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES')} minutes")
```
