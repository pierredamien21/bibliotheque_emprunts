# 📚 Documentation API - Système de Gestion de Bibliothèque (V2)

Bienvenue dans la documentation officielle de votre plateforme de bibliothèque. Ce document explique simplement comment utiliser les fonctionnalités, qui peut faire quoi, et comment naviguer dans l'API.

---

## 👥 1. Qui peut faire quoi ? (Rôles)

L'accès à l'API est protégé par trois niveaux de sécurité :

| Rôle | Description | Actions Clés |
| :--- | :--- | :--- |
| **🛡️ Administrateur** | Le "Super-Patron" | Gérer le personnel (Bibliothécaires), configurer les règles globales. |
| **📖 Agent (Staff)** | Le Gestionnaire | Inscrire des membres, enregistrer les prêts/retours, voir les statistiques. |
| **👤 Membre** | L'Utilisateur final | Réserver des livres, prolonger ses prêts, laisser des avis, gérer ses favoris. |

---

## 🚀 2. Guide de Démarrage Rapide

### 🔐 Connexion
Pour utiliser l'API, vous devez d'abord obtenir un "Pass" (Token JWT) :
- **Personnel** : `POST /auth/login` (utilisez login/mot de passe).
- **Membres** : `POST /auth/login/member` (utilisez email/login/numéro de carte).

### 🔍 Mon Profil
Utilisez l'endpoint `GET /auth/me` pour voir instantanément vos informations et votre rôle une fois connecté.

---

## 📖 3. Fonctionnalités pour les UTILISATEURS (Membres)

### 📚 Explorer le Catalogue
- **Recherche Avancée** : `GET /livres/` (Filtrez par titre ou catégorie).
- **Disponibilité** : Le champ `nb_disponible` vous indique en temps réel s'il reste des exemplaires en stock.

### 📅 Gérer ses Emprunts
- **Réservation Libres** : `POST /reservations/`. Vous pouvez réserver un livre tout seul !
- **Prolongation (Renewal)** : `PATCH /emprunts/{id}/prolonger`. Gagnez **7 jours de plus** sur votre prêt (si le livre n'est pas réservé par quelqu'un d'autre).

### ⭐ Interaction et Favoris
- **Avis** : `POST /avis/`. Donnez une note de 1 à 5 et laissez un commentaire sur vos lectures.
- **Favoris** : `POST /favoris/`. Marquez des livres pour les retrouver plus tard.
- **Notifications** : `GET /notifications/`. Restez informé de vos retours validés ou de vos éventuelles amendes.

---

## 🛡️ 4. Fonctionnalités pour le PERSONNEL (Staff/Admin)

### 🖼️ Gestion des Images
- **Upload Couverture** : `POST /upload/livre/{id_livre}`. Permet d'uploader une image (JPG, PNG) pour la couverture du livre. L'image sera stockée localement sur le serveur.

### 📦 Gestion des Flux
- **Emprunts** : `POST /emprunts/`. Enregistrez un prêt au comptoir.
- **Retours & Amendes** : `PUT /emprunts/{id}/retour`. Le système calcule **automatiquement** l'amende de retard (100 FCFA / jour) et crée une sanction si nécessaire.

### 🗑️ Administration Sécurisée
- **Suppression Membre** : Interdite si le membre a des emprunts en cours.
- **Suppression Bibliothèque** : Réservée à l'Admin, interdite si le personnel est lié à des transactions historiques.

### 📊 Tableau de Bord (Analytics)
Accédez à `GET /stats/` pour voir :
- Le **Top 5 des livres** les plus populaires.
- La répartition des livres par **Catégorie**.
- Les indicateurs globaux (retards, total membres, etc.).

---

## 🛠️ 5. Aide Technique (Swagger)

1. Ouvrez votre navigateur sur : `https://bibliotheque-emprunts.onrender.com/docs`.
2. Cliquez sur **"Authorize"** et entrez votre Token ou identifiants.
3. Testez les endpoints directement avec le bouton **"Try it out"**.

---
> [!TIP]
> **Une question ?** Regardez les messages d'erreur de l'API, ils sont conçus pour être explicites (ex: "Limite d'emprunts atteinte", "Livre déjà réservé").
