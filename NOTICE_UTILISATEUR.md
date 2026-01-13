# 📖 Manuel de l'Utilisateur - API Bibliothèque (V3)

Ce guide détaille toutes les actions possibles via l'API, classées par modules et par rôles.

---

## 🔐 1. Authentification & Accès

### Connexion Unifiée
**Endpoint** : `POST /auth/login/unified`  
**Utilisation** : C'est la porte d'entrée principale. Elle accepte les identifiants du personnel et des membres.  
- **Staff** : Utilisez votre `login`.  
- **Membres** : Utilisez votre `email`, `login` ou `numéro de carte`.

### Voir son Profil
**Endpoint** : `GET /auth/me`  
**Description** : Retourne vos informations personnelles, votre rôle et vos permissions actuelles. Indispensable pour récupérer votre `id_membre`.

---

## 📚 2. Gestion du Catalogue (L'Inventaire)

### Livres
- **Lister/Rechercher** : `GET /livres/`  
  - Filtres : par `titre` ou `id_categorie`.  
  - Bonus : Affiche `nb_disponible` pour chaque livre.
- **Détails** : `GET /livres/{id}` : Fiche complète d'un livre.
- **Ajouter/Modifier** : `POST` ou `PUT /livres/` (Réservé au Staff).
- **Supprimer** : `DELETE /livres/{id}` (Réservé au Staff).

### Auteurs & Catégories
- **Auteurs** : `GET /auteurs/` (Voir tous), `POST /auteurs/` (Ajouter).
- **Catégories** : `GET /categories/` (Voir tous), `POST /categories/` (Ajouter).

### Recommandations IA
**Endpoint** : `GET /livres/recommandations`  
**Description** : Propose 5 livres personnalisés basés sur vos lectures passées et vos thèmes favoris.

---

## 📦 3. Gestion Physique (Exemplaires & Images)

### Exemplaires
**Description** : Un livre peut avoir plusieurs exemplaires physiques (un neuf, un usé, etc.).  
- **Gérer** : `GET`, `POST`, `PUT /exemplaires/`.  
- **États** : Disponible, Emprunté, Perdu, En réparation.

### Images de Couverture
**Endpoint** : `POST /upload/livre/{id_livre}`  
**Description** : Uploadez une image (JPG/PNG). Elle sera automatiquement liée au livre et servira de couverture sur le frontend.

---

## 👥 4. Membres & Comptes

### Inscription & Gestion
- **Inscrire un membre** : `POST /membres/` (Staff).
- **Modifier un compte** : `PUT /membres/{id}`.
- **Types de Membres** : `GET /types-membre/`. Définit les règles (nb max de livres, durée du prêt).

---

## 📅 5. Le Cycle de l'Emprunt (Actions Clés)

### Pour le STAFF (Action au comptoir)
1. **Créer un Emprunt** : `POST /emprunts/`.  
   - Nécessite : `id_membre`, `id_exemplaire`.  
   - La date de retour est calculée automatiquement.
2. **Gérer un Retour** : `PUT /emprunts/{id}/retour`.  
   - Clôture le prêt.  
   - **Important** : Calcule automatiquement les amendes (100 FCFA/jour) en cas de retard.

### Pour le MEMBRE (Self-service)
- **Mes Emprunts** : `GET /emprunts/mes-emprunts`.  
- **Prolonger** : `PATCH /emprunts/{id}/prolonger`. Gagnez 7 jours de plus (possible 1 seule fois, si le livre n'est pas réservé).

---

## 🔔 6. Réservations, Favoris & Sanctions

### Réservations
- **Réserver** : `POST /reservations/`.  
- **Mes Réservations** : `GET /reservations/mes-reservations`.
- **Statuts** : En attente, Confirmée, Annulée.

### Sanctions (Amendes)
- **Voir ses amendes** : `GET /sanctions/mes-sanctions`.
- **Payer** : `PATCH /sanctions/{id}/statut` (Status : Payée).

### Favoris
**Endpoints** : `POST /favoris/` et `GET /favoris/`.  
Marquez vos futurs lectures !

---

## 📨 7. Communication & Avis

### Messagerie Interne (Chat)
- **Membre** : `POST /messages/` pour poser une question.
- **Staff** : `PATCH /messages/{id}/repondre` pour répondre au membre.
- **Historique** : `GET /messages/`.

### Avis & Notes
- **Laisser un avis** : `POST /avis/` (Note de 1 à 5).
- **Consulter** : `GET /avis/livre/{id}`.

### Notifications
**Endpoint** : `GET /notifications/`. Alertes sur les retours validés, les amendes générées ou les réservations prêtes.

---

## 📊 8. Statistiques (Dashboard Staff)

**Endpoint** : `GET /stats/`  
Fournit des données clés :
- Top 5 des livres les plus lus.
- Nombre total d'emprunts par catégorie.
- Indicateurs de performance de la bibliothèque.

---

### 💡 Rappel Sécurité
Toutes les routes (sauf la consultation simple du catalogue) nécessitent d'être **Connecté**. 
Utilisez le bouton **Authorize** dans Swagger avec votre Token JWT.
