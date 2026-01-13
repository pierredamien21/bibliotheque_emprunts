
-- ============================================
-- MPD PostgreSQL - Gestion Bibliothèque (FINAL)
-- ============================================

BEGIN;

-- =========================
-- TABLE: TYPE_MEMBRE
-- =========================
CREATE TABLE type_membre (
    id_type_membre SERIAL PRIMARY KEY,
    nom_type VARCHAR(50) NOT NULL,
    duree_max_emprunt INT NOT NULL CHECK (duree_max_emprunt > 0),
    nb_max_emprunt INT NOT NULL CHECK (nb_max_emprunt > 0)
);

-- =========================
-- TABLE: MEMBRE
-- =========================
CREATE TABLE membre (
    id_membre SERIAL PRIMARY KEY,
    numero_carte VARCHAR(30) UNIQUE NOT NULL,
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    telephone VARCHAR(30),
    adresse TEXT,
    date_naissance DATE,
    date_inscription DATE NOT NULL DEFAULT CURRENT_DATE,
    statut_compte VARCHAR(20) NOT NULL CHECK (statut_compte IN ('Actif', 'Suspendu')),
    login VARCHAR(50) UNIQUE,
    mot_de_passe_hash TEXT,
    derniere_connexion TIMESTAMP,
    id_type_membre INT NOT NULL,
    CONSTRAINT fk_membre_type
        FOREIGN KEY (id_type_membre)
        REFERENCES type_membre(id_type_membre)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

-- =========================
-- TABLE: BIBLIOTHECAIRE
-- =========================
CREATE TABLE bibliothecaire (
    id_bibliotecaire SERIAL PRIMARY KEY,
    matricule VARCHAR(30) UNIQUE NOT NULL,
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    telephone VARCHAR(30),
    login VARCHAR(50) UNIQUE NOT NULL,
    mot_de_passe_hash TEXT NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('Admin', 'Agent'))
);

-- =========================
-- TABLE: CATEGORIE
-- =========================
CREATE TABLE categorie (
    id_categorie SERIAL PRIMARY KEY,
    nom_categorie VARCHAR(100) NOT NULL,
    description TEXT
);

-- =========================
-- TABLE: AUTEUR
-- =========================
CREATE TABLE auteur (
    id_auteur SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL
);

-- =========================
-- TABLE: LIVRE
-- =========================
CREATE TABLE livre (
    id_livre SERIAL PRIMARY KEY,
    titre VARCHAR(200) NOT NULL,
    descriptions TEXT,
    isbn VARCHAR(30) UNIQUE,
    editeur VARCHAR(150),
    langue VARCHAR(50),
    annee_publication INT CHECK (annee_publication >= 0),
    date_ajout_catalogue DATE NOT NULL DEFAULT CURRENT_DATE,
    id_categorie INT NOT NULL,
    image_url VARCHAR(500),
    CONSTRAINT fk_livre_categorie
        FOREIGN KEY (id_categorie)
        REFERENCES categorie(id_categorie)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

-- =========================
-- TABLE: LIVRE_AUTEUR (N-N)
-- =========================
CREATE TABLE livre_auteur (
    id_livre INT NOT NULL,
    id_auteur INT NOT NULL,
    PRIMARY KEY (id_livre, id_auteur),
    CONSTRAINT fk_la_livre
        FOREIGN KEY (id_livre)
        REFERENCES livre(id_livre)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    CONSTRAINT fk_la_auteur
        FOREIGN KEY (id_auteur)
        REFERENCES auteur(id_auteur)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

-- =========================
-- TABLE: EXEMPLAIRE
-- =========================
CREATE TABLE exemplaire (
    id_exemplaire SERIAL PRIMARY KEY,
    code_barre VARCHAR(50) UNIQUE NOT NULL,
    etat VARCHAR(20) NOT NULL CHECK (etat IN ('Disponible', 'Emprunte', 'Reserve', 'Abime')),
    statut_logique VARCHAR(20) NOT NULL CHECK (statut_logique IN ('Actif', 'Retire')),
    date_acquisition DATE,
    localisation VARCHAR(100),
    id_livre INT NOT NULL,
    CONSTRAINT fk_exemplaire_livre
        FOREIGN KEY (id_livre)
        REFERENCES livre(id_livre)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

-- =========================
-- TABLE: EMPRUNT
-- =========================
CREATE TABLE emprunt (
    id_emprunt SERIAL PRIMARY KEY,
    date_emprunt DATE NOT NULL DEFAULT CURRENT_DATE,
    date_retour_prevue DATE, -- calculée par trigger
    date_retour_effective DATE,
    statut VARCHAR(20) NOT NULL CHECK (statut IN ('En cours', 'Termine', 'Retard')),
    renouvellement_count INT NOT NULL DEFAULT 0 CHECK (renouvellement_count >= 0),
    commentaire TEXT,
    id_membre INT NOT NULL,
    id_exemplaire INT NOT NULL,
    id_bibliotecaire INT NOT NULL,
    CONSTRAINT fk_emprunt_membre
        FOREIGN KEY (id_membre)
        REFERENCES membre(id_membre)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT fk_emprunt_exemplaire
        FOREIGN KEY (id_exemplaire)
        REFERENCES exemplaire(id_exemplaire)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT fk_emprunt_bibliothecaire
        FOREIGN KEY (id_bibliotecaire)
        REFERENCES bibliothecaire(id_bibliotecaire)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

-- =========================
-- TABLE: RESERVATION
-- =========================
CREATE TABLE reservation (
    id_reservation SERIAL PRIMARY KEY,
    date_reservation DATE NOT NULL DEFAULT CURRENT_DATE,
    statut VARCHAR(20) NOT NULL CHECK (statut IN ('En attente', 'Confirmee', 'Annulee')),
    priorite INT NOT NULL CHECK (priorite > 0),
    id_membre INT NOT NULL,
    id_livre INT NOT NULL,
    id_bibliotecaire INT,
    CONSTRAINT fk_reservation_membre
        FOREIGN KEY (id_membre)
        REFERENCES membre(id_membre)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT fk_reservation_livre
        FOREIGN KEY (id_livre)
        REFERENCES livre(id_livre)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT fk_reservation_bibliothecaire
        FOREIGN KEY (id_bibliotecaire)
        REFERENCES bibliothecaire(id_bibliotecaire)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

-- =========================
-- TABLE: SANCTION
-- =========================
CREATE TABLE sanction (
    id_sanction SERIAL PRIMARY KEY,
    type_sanction VARCHAR(30) NOT NULL CHECK (type_sanction IN ('Retard', 'Perte', 'Dommage')),
    montant NUMERIC(10,2) CHECK (montant >= 0),
    date_sanction DATE NOT NULL DEFAULT CURRENT_DATE,
    date_fin_suspension DATE,
    statut VARCHAR(20) NOT NULL CHECK (statut IN ('Payee', 'Non payee')),
    id_membre INT NOT NULL,
    id_emprunt INT NOT NULL,
    id_bibliotecaire INT NOT NULL,
    CONSTRAINT fk_sanction_membre
        FOREIGN KEY (id_membre)
        REFERENCES membre(id_membre)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT fk_sanction_emprunt
        FOREIGN KEY (id_emprunt)
        REFERENCES emprunt(id_emprunt)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT fk_sanction_bibliothecaire
        FOREIGN KEY (id_bibliotecaire)
        REFERENCES bibliothecaire(id_bibliotecaire)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

-- =========================
-- TABLE: AVIS
-- =========================
CREATE TABLE avis (
    id_avis SERIAL PRIMARY KEY,
    note INT NOT NULL CHECK (note >= 1 AND note <= 5),
    commentaire TEXT,
    date_avis DATE NOT NULL DEFAULT CURRENT_DATE,
    id_membre INT NOT NULL,
    id_livre INT NOT NULL,
    CONSTRAINT fk_avis_membre FOREIGN KEY (id_membre) REFERENCES membre(id_membre) ON DELETE CASCADE,
    CONSTRAINT fk_avis_livre FOREIGN KEY (id_livre) REFERENCES livre(id_livre) ON DELETE CASCADE
);

-- =========================
-- TABLE: FAVORIS
-- =========================
CREATE TABLE favoris (
    id_membre INT NOT NULL,
    id_livre INT NOT NULL,
    PRIMARY KEY (id_membre, id_livre),
    CONSTRAINT fk_favoris_membre FOREIGN KEY (id_membre) REFERENCES membre(id_membre) ON DELETE CASCADE,
    CONSTRAINT fk_favoris_livre FOREIGN KEY (id_livre) REFERENCES livre(id_livre) ON DELETE CASCADE
);

-- =========================
-- TABLE: NOTIFICATION
-- =========================
CREATE TABLE notification (
    id_notification SERIAL PRIMARY KEY,
    message TEXT NOT NULL,
    date_notif TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    lu BOOLEAN NOT NULL DEFAULT FALSE,
    id_membre INT NOT NULL,
    CONSTRAINT fk_notification_membre FOREIGN KEY (id_membre) REFERENCES membre(id_membre) ON DELETE CASCADE
);

-- =========================
-- TABLE: MESSAGE (V3)
-- =========================
CREATE TABLE message (
    id_message SERIAL PRIMARY KEY,
    id_membre INT NOT NULL,
    id_bibliotecaire INT,
    contenu TEXT NOT NULL,
    reponse TEXT,
    date_envoi TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    date_reponse TIMESTAMP,
    statut VARCHAR(20) NOT NULL DEFAULT 'Envoye',
    CONSTRAINT fk_message_membre FOREIGN KEY (id_membre) REFERENCES membre(id_membre) ON DELETE CASCADE,
    CONSTRAINT fk_message_bibliothecaire FOREIGN KEY (id_bibliotecaire) REFERENCES bibliothecaire(id_bibliotecaire)
);

COMMIT;
