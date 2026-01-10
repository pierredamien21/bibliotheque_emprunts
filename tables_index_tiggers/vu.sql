-- ============================================
-- VUES - Gestion Bibliothèque
-- PostgreSQL
-- ============================================

BEGIN;

-- =================================================
-- 1. EXEMPLAIRES DISPONIBLES
-- =================================================
CREATE OR REPLACE VIEW vue_exemplaires_disponibles AS
SELECT
    e.id_exemplaire,
    e.code_barre,
    l.id_livre,
    l.titre,
    c.nom_categorie,
    e.localisation
FROM exemplaire e
JOIN livre l ON e.id_livre = l.id_livre
JOIN categorie c ON l.id_categorie = c.id_categorie
WHERE e.etat = 'Disponible'
  AND e.statut_logique = 'Actif';


-- =================================================
-- 2. EMPRUNTS EN RETARD
-- =================================================
CREATE OR REPLACE VIEW vue_emprunts_retard AS
SELECT
    em.id_emprunt,
    m.numero_carte,
    m.nom,
    m.prenom,
    l.titre,
    em.date_emprunt,
    em.date_retour_prevue,
    (CURRENT_DATE - em.date_retour_prevue) AS jours_retard
FROM emprunt em
JOIN membre m ON em.id_membre = m.id_membre
JOIN exemplaire e ON em.id_exemplaire = e.id_exemplaire
JOIN livre l ON e.id_livre = l.id_livre
WHERE em.statut = 'Retard';


-- =================================================
-- 3. LIVRES LES PLUS EMPRUNTÉS
-- =================================================
CREATE OR REPLACE VIEW vue_livres_plus_empruntes AS
SELECT
    l.id_livre,
    l.titre,
    COUNT(em.id_emprunt) AS nb_emprunts
FROM livre l
JOIN exemplaire e ON l.id_livre = e.id_livre
JOIN emprunt em ON e.id_exemplaire = em.id_exemplaire
GROUP BY l.id_livre, l.titre
ORDER BY nb_emprunts DESC;


-- =================================================
-- 4. HISTORIQUE DES EMPRUNTS PAR MEMBRE
-- =================================================
CREATE OR REPLACE VIEW vue_historique_emprunts AS
SELECT
    m.id_membre,
    m.numero_carte,
    m.nom,
    m.prenom,
    l.titre,
    em.date_emprunt,
    em.date_retour_effective,
    em.statut
FROM membre m
JOIN emprunt em ON m.id_membre = em.id_membre
JOIN exemplaire e ON em.id_exemplaire = e.id_exemplaire
JOIN livre l ON e.id_livre = l.id_livre
ORDER BY m.id_membre, em.date_emprunt DESC;


-- =================================================
-- 5. STATISTIQUES PAR CATEGORIE
-- =================================================
CREATE OR REPLACE VIEW vue_stats_categorie AS
SELECT
    c.id_categorie,
    c.nom_categorie,
    COUNT(DISTINCT l.id_livre) AS nb_livres,
    COUNT(em.id_emprunt) AS nb_emprunts
FROM categorie c
LEFT JOIN livre l ON c.id_categorie = l.id_categorie
LEFT JOIN exemplaire e ON l.id_livre = e.id_livre
LEFT JOIN emprunt em ON e.id_exemplaire = em.id_exemplaire
GROUP BY c.id_categorie, c.nom_categorie
ORDER BY nb_emprunts DESC;


-- =================================================
-- 6. EMPRUNTS EN COURS PAR MEMBRE (API)
-- =================================================
CREATE OR REPLACE VIEW vue_emprunts_en_cours_membre AS
SELECT
    m.id_membre,
    m.numero_carte,
    l.titre,
    e.code_barre,
    em.date_emprunt,
    em.date_retour_prevue
FROM emprunt em
JOIN membre m ON em.id_membre = m.id_membre
JOIN exemplaire e ON em.id_exemplaire = e.id_exemplaire
JOIN livre l ON e.id_livre = l.id_livre
WHERE em.statut IN ('En cours', 'Retard');


-- =================================================
-- 7. FILE D’ATTENTE DES RESERVATIONS PAR LIVRE
-- =================================================
CREATE OR REPLACE VIEW vue_file_reservation_livre AS
SELECT
    r.id_reservation,
    l.titre,
    m.numero_carte,
    m.nom,
    r.date_reservation,
    r.priorite,
    r.statut
FROM reservation r
JOIN livre l ON r.id_livre = l.id_livre
JOIN membre m ON r.id_membre = m.id_membre
WHERE r.statut = 'En attente'
ORDER BY l.id_livre, r.priorite, r.date_reservation;


-- =================================================
-- 8. SANCTIONS ACTIVES PAR MEMBRE
-- =================================================
CREATE OR REPLACE VIEW vue_sanctions_actives AS
SELECT
    s.id_sanction,
    m.numero_carte,
    m.nom,
    s.type_sanction,
    s.montant,
    s.date_sanction,
    s.statut
FROM sanction s
JOIN membre m ON s.id_membre = m.id_membre
WHERE s.statut = 'Non payee';


COMMIT;
