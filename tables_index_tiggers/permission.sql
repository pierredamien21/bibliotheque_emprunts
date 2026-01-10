-- ============================================
-- PERMISSIONS & ROLES - Gestion Bibliothèque
-- PostgreSQL
-- ============================================

BEGIN;

-- =========================
-- NETTOYAGE (si déjà créés)
-- =========================
DROP ROLE IF EXISTS agent_biblio;
DROP ROLE IF EXISTS api_user;

DROP ROLE IF EXISTS role_agent;
DROP ROLE IF EXISTS role_api;


-- =========================
-- ROLES LOGIQUES
-- =========================
CREATE ROLE role_agent NOINHERIT;
CREATE ROLE role_api NOINHERIT;


-- =========================
-- UTILISATEURS
-- =========================
CREATE USER agent_biblio WITH PASSWORD 'AGENT_STRONG_PASSWORD';
GRANT role_agent TO agent_biblio;

CREATE USER api_user WITH PASSWORD 'API_STRONG_PASSWORD';
GRANT role_api TO api_user;


-- =========================
-- DROITS AGENT BIBLIOTHEQUE
-- =========================

-- lecture complète
GRANT SELECT ON ALL TABLES IN SCHEMA public TO role_agent;
GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO role_agent;

-- écriture métier
GRANT INSERT, UPDATE ON
    type_membre,
    membre,
    bibliothecaire,
    categorie,
    auteur,
    livre,
    livre_auteur,
    exemplaire,
    emprunt,
    reservation,
    sanction
TO role_agent;


-- =========================
-- DROITS API
-- =========================

-- consultation
GRANT SELECT ON
    membre,
    livre,
    auteur,
    categorie,
    exemplaire,
    vue_exemplaires_disponibles,
    vue_emprunts_en_cours_membre,
    vue_file_reservation_livre
TO role_api;

-- opérations autorisées
GRANT INSERT, UPDATE ON
    emprunt,
    reservation
TO role_api;

-- jamais supprimer
REVOKE DELETE ON ALL TABLES IN SCHEMA public FROM role_api;

-- sequences pour INSERT
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO role_api;


-- =========================
-- PRIVILEGES FUTURS
-- =========================

ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT SELECT, INSERT, UPDATE ON TABLES TO role_agent;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT SELECT, INSERT, UPDATE ON TABLES TO role_api;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT USAGE, SELECT ON SEQUENCES TO role_agent, role_api;

COMMIT;
