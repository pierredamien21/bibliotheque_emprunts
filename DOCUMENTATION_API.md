# Documentation de l'API - Système de Gestion de Bibliothèque

Cette documentation détaille le fonctionnement de l'API, les rôles des utilisateurs, et les processus d'authentification.

## 1. Rôles et Permissions

L'API utilise un système de Contrôle d'Accès Basé sur les Rôles (RBAC) avec trois niveaux :

### 🔐 Administrateur (Admin)
*   **Identifiant par défaut** : `admin` / `admin123`
*   **Pouvoirs** : Accès total à tout le système.
*   **Exclusivité** : C'est le seul rôle autorisé à gérer les comptes du personnel (les Bibliothécaires).
*   **Router spécifique** : `routers/bibliotecaire.py`

### 🛡️ Agent de Bibliothèque (Agent)
*   **Rôle** : Gestion quotidienne de la bibliothèque.
*   **Pouvoirs** : 
    *   Gestion des livres, auteurs, catégories et exemplaires.
    *   **Inscrire les membres**.
    *   Enregistrer les emprunts et les retours.
    *   Gérer les réservations et les sanctions.
*   **Router spécifique** : Presque tous les routers (`livre`, `emprunt`, `membre`, etc.).

### 📖 Membre (Membre)
*   **Rôle** : Utilisateur final (lecteur).
*   **Pouvoirs** : 
    *   Consulter le catalogue (livres, auteurs).
    *   Voir **uniquement son propre historique** d'emprunts.
*   **Restrictions** : Ne peut pas modifier la base de données ni voir les données des autres membres.

---

## 2. Le Cycle de Vie d'un Membre

Le processus d'accès pour un membre suit ces étapes précises :

### Étape 1 : Création par le Staff (Agent/Admin)
Le membre ne peut pas s'inscrire tout seul. C'est un bibliothécaire qui remplit le formulaire :
*   **Endpoint** : `POST /membres/`
*   **Données requises** : Nom, prénom, email, numero_carte, **login** et **mot de passe**.
*   **ID Type Membre** : Doit correspondre à un type existant (ex: 1 pour Étudiant).

### Étape 2 : Identifiants
Une fois le compte créé, le membre possède trois clés pour s'identifier (au choix) :
1.  Son **Email**
2.  Son **Login**
3.  Son **Numéro de carte**

### Étape 3 : Connexion (Login)
Le membre utilise l'endpoint dédié à la plateforme publique :
*   **Endpoint** : `POST /auth/login/member`
*   **Retour** : Un jeton **JWT** (Token) qu'il devra fournir dans l'en-tête `Authorization: Bearer <token>` pour ses prochaines requêtes.

---

## 3. Détail des Routers et Fonctionnalités

### 🔑 Authentication (`/auth`)
*   `POST /auth/login` : Connexion pour le Staff uniquement.
*   `POST /auth/login/member` : Connexion pour les Membres uniquement.

### 👥 Membres (`/membres`)
*   `POST /` : (Staff) Inscription d'un nouveau membre.
*   `GET /` : (Staff) Liste de tous les membres.
*   `PATCH /{id}/statut` : (Staff) Suspendre ou réactiver un compte.

### 📚 Catalogue (`/livres`, `/auteurs`, `/categories`)
*   `GET /` : (Public/Membre/Staff) Voir le catalogue.
*   `POST`, `PUT`, `DELETE` : (Staff uniquement) Modifier le catalogue.

### 📦 Emprunts (`/emprunts`)
*   `POST /` : (Staff) Enregistrer un prêt quand le membre est au comptoir.
*   `PUT /{id}/retour` : (Staff) Enregistrer le retour d'un livre.
*   `GET /membre/{id_membre}` : (Membre ou Staff). Un membre ne peut voir que son propre ID ici. Si un membre tente de voir l'ID d'un autre, il recevra une erreur `403 Forbidden`.

### 📅 Réservations et Sanctions
*   Gestion réservée au **Staff** pour assurer l'intégrité des règles de la bibliothèque.

---

## 4. Comment tester avec Swagger (`/docs`)

1.  Lancez le serveur.
2.  Allez sur `http://localhost:8000/docs`.
3.  Cliquez sur le bouton **Authorize** en haut à droite.
4.  Entrez les identifiants Admin/Agent pour débloquer les fonctions de gestion.
5.  Pour tester en tant que membre, déconnectez-vous et utilisez les identifiants générés par `POST /auth/login/member`.
