-- ============================================
-- INDEX COMPLETS - Gestion Bibliothèque
-- PostgreSQL
-- ============================================

BEGIN;

-- =========================
-- MEMBRE
-- =========================
CREATE UNIQUE INDEX IF NOT EXISTS idx_membre_numero_carte
ON membre(numero_carte);

CREATE INDEX IF NOT EXISTS idx_membre_nom_prenom
ON membre(nom, prenom);

CREATE INDEX IF NOT EXISTS idx_membre_statut_actif
ON membre(statut_compte)
WHERE statut_compte = 'Actif';


-- =========================
-- TYPE_MEMBRE
-- =========================
CREATE INDEX IF NOT EXISTS idx_type_membre_id
ON type_membre(id_type_membre);


-- =========================
-- LIVRE / AUTEUR / CATEGORIE
-- =========================
CREATE INDEX IF NOT EXISTS idx_livre_titre
ON livre(titre);

CREATE UNIQUE INDEX IF NOT EXISTS idx_livre_isbn
ON livre(isbn);

CREATE INDEX IF NOT EXISTS idx_livre_id_categorie
ON livre(id_categorie);

CREATE INDEX IF NOT EXISTS idx_auteur_nom_prenom
ON auteur(nom, prenom);


-- =========================
-- LIVRE_AUTEUR
-- =========================
CREATE INDEX IF NOT EXISTS idx_la_livre
ON livre_auteur(id_livre);

CREATE INDEX IF NOT EXISTS idx_la_auteur
ON livre_auteur(id_auteur);


-- =========================
-- EXEMPLAIRE
-- =========================
CREATE UNIQUE INDEX IF NOT EXISTS idx_exemplaire_code_barre
ON exemplaire(code_barre);

CREATE INDEX IF NOT EXISTS idx_exemplaire_disponible
ON exemplaire(etat)
WHERE etat = 'Disponible';

CREATE INDEX IF NOT EXISTS idx_exemplaire_livre
ON exemplaire(id_livre);


-- =========================
-- EMPRUNT (CRITIQUE)
-- =========================
CREATE INDEX IF NOT EXISTS idx_emprunt_membre_actifs
ON emprunt(id_membre)
WHERE statut IN ('En cours', 'Retard');

CREATE INDEX IF NOT EXISTS idx_emprunt_exemplaire_actifs
ON emprunt(id_exemplaire)
WHERE statut IN ('En cours', 'Retard');

CREATE INDEX IF NOT EXISTS idx_emprunt_retard
ON emprunt(date_retour_prevue)
WHERE statut = 'Retard';

CREATE INDEX IF NOT EXISTS idx_emprunt_membre_date
ON emprunt(id_membre, date_emprunt DESC);


-- =========================
-- RESERVATION
-- =========================
CREATE INDEX IF NOT EXISTS idx_reservation_livre_attente
ON reservation(id_livre)
WHERE statut = 'En attente';

CREATE INDEX IF NOT EXISTS idx_reservation_membre
ON reservation(id_membre);


-- =========================
-- SANCTION
-- =========================
CREATE INDEX IF NOT EXISTS idx_sanction_impayee
ON sanction(id_membre)
WHERE statut = 'Non payee';

CREATE INDEX IF NOT EXISTS idx_sanction_emprunt
ON sanction(id_emprunt);


-- =========================
-- FULL TEXT SEARCH (OPTIONNEL)
-- =========================
CREATE INDEX IF NOT EXISTS idx_livre_fulltext
ON livre
USING GIN (to_tsvector('french', titre || ' ' || COALESCE(descriptions,'')));

COMMIT;
