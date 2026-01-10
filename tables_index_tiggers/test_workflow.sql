-- Test workflow pour la base de données de la bibliothèque
-- But: valider triggers (emprunt, retour), reservation, contraintes
-- Exécuter sur une base de test (pas en production).

-- IMPORTANT: exécuter après avoir appliqué `table.sql`, `tiggers.sql`, `vu.sql`.

-- Exemple d'exécution :
-- psql -h <host> -U <user> -d <db> -f table.sql
-- psql -h <host> -U <user> -d <db> -f tiggers.sql
-- psql -h <host> -U <user> -d <db> -f vu.sql
-- psql -h <host> -U <user> -d <db> -f test_workflow.sql

-- Ce script utilise des DO blocks pour capturer erreurs attendues et affiche l'état.

-- 1) Création d'éléments de test
-- 1) Création d'éléments de test (insertion conditionnelle si nécessaire)
DO $$
DECLARE
    v_type INT;
    v_membre INT;
    v_biblio INT;
    v_categ INT;
    v_auteur INT;
    v_livre INT;
    v_ex INT;
    v_emprunt INT;
BEGIN
    -- Insérer le type_membre s'il n'existe pas, puis récupérer son id
    PERFORM 1 FROM type_membre WHERE nom_type='Standard';
    IF NOT FOUND THEN
        INSERT INTO type_membre (nom_type, duree_max_emprunt, nb_max_emprunt)
        VALUES ('Standard', 14, 2);
    END IF;

    SELECT id_type_membre INTO v_type FROM type_membre WHERE nom_type='Standard' LIMIT 1;

    -- Créer membre
    INSERT INTO membre (numero_carte, nom, prenom, email, statut_compte, id_type_membre)
    VALUES ('CARTETST1', 'Dupont', 'Jean', 'jean.dupont@example.test', 'Actif', v_type)
    RETURNING id_membre INTO v_membre;

    -- Créer bibliothécaire
    INSERT INTO bibliothecaire (matricule, nom, prenom, email, login, mot_de_passe_hash, role)
    VALUES ('BIB1', 'Leclerc', 'Anne', 'anne.leclerc@example.test', 'anne', 'hash', 'Agent')
    RETURNING id_bibliotecaire INTO v_biblio;

    -- Categorie, auteur, livre, exemplaire
    INSERT INTO categorie (nom_categorie) VALUES ('Test') RETURNING id_categorie INTO v_categ;
    INSERT INTO auteur (nom, prenom) VALUES ('Martin','Paul') RETURNING id_auteur INTO v_auteur;
    INSERT INTO livre (titre, id_categorie) VALUES ('Livre Test', v_categ) RETURNING id_livre INTO v_livre;
    INSERT INTO livre_auteur (id_livre, id_auteur) VALUES (v_livre, v_auteur);
    INSERT INTO exemplaire (code_barre, etat, statut_logique, id_livre) VALUES ('CB-001','Disponible','Actif',v_livre) RETURNING id_exemplaire INTO v_ex;

    RAISE NOTICE 'Création ok: membre=%, exemplaire=%', v_membre, v_ex;

    -- 2) Emprunt valide
    INSERT INTO emprunt (date_emprunt, id_membre, id_exemplaire, id_bibliotecaire)
    VALUES (CURRENT_DATE, v_membre, v_ex, v_biblio)
    RETURNING id_emprunt INTO v_emprunt;

    RAISE NOTICE 'Emprunt créé id=%', v_emprunt;

    -- Vérifier que l'exemplaire est marqué 'Emprunte'
    PERFORM 1 FROM exemplaire WHERE id_exemplaire=v_ex AND etat='Emprunte';
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Exemplaire non marqué Emprunte après insertion emprunt';
    ELSE
        RAISE NOTICE 'Trigger after_insert_emprunt OK';
    END IF;

    -- 3) Tentative d'emprunt du même exemplaire => doit échouer
    BEGIN
        INSERT INTO emprunt (date_emprunt, id_membre, id_exemplaire, id_bibliotecaire)
        VALUES (CURRENT_DATE, v_membre, v_ex, v_biblio);
        RAISE EXCEPTION 'Erreur attendue non levée : double emprunt';
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE 'Double emprunt bloqué (attendu): %', SQLERRM;
    END;

    -- 4) Retour: mettre statut 'Termine' et verifier exemplaire redevenu 'Disponible'
    UPDATE emprunt SET statut='Termine', date_retour_effective=CURRENT_DATE WHERE id_emprunt=v_emprunt;
    PERFORM 1 FROM exemplaire WHERE id_exemplaire=v_ex AND etat='Disponible';
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Exemplaire non remis Disponible après retour';
    ELSE
        RAISE NOTICE 'Trigger after_update_emprunt OK';
    END IF;

    -- 5) Reservation: créer une reservation valide
    INSERT INTO reservation (id_membre, id_livre, id_bibliotecaire, priorite)
    VALUES (v_membre, v_livre, v_biblio, 1);
    RAISE NOTICE 'Reservation insérée OK';

EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'Erreur lors du test: %', SQLERRM;
    RAISE;
END;
$$;

-- Nettoyage optionnel: commenter si vous voulez garder les données pour inspection
-- DELETE FROM reservation WHERE id_membre IN (SELECT id_membre FROM membre WHERE numero_carte='CARTETST1');
-- DELETE FROM emprunt WHERE id_membre IN (SELECT id_membre FROM membre WHERE numero_carte='CARTETST1');
-- DELETE FROM exemplaire WHERE code_barre='CB-001';
-- DELETE FROM livre WHERE id_livre IN (SELECT id_livre FROM livre WHERE titre='Livre Test');
-- DELETE FROM auteur WHERE nom='Martin' AND prenom='Paul';
-- DELETE FROM categorie WHERE id_categorie IN (SELECT id_categorie FROM categorie WHERE nom_categorie='Test');
-- DELETE FROM bibliothecaire WHERE matricule='BIB1';
-- DELETE FROM membre WHERE numero_carte='CARTETST1';

-- Fin du script
