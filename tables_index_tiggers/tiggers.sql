CREATE OR REPLACE FUNCTION trg_before_insert_emprunt_fn()
RETURNS TRIGGER AS $$
DECLARE
    nb_actuel INT;
    nb_max INT;
    duree INT;
    etat_exemplaire VARCHAR;
BEGIN
    -- Membre actif ?
    IF (SELECT statut_compte FROM membre WHERE id_membre = NEW.id_membre) <> 'Actif' THEN
        RAISE EXCEPTION 'Emprunt refusé : membre suspendu';
    END IF;

    -- Exemplaire disponible ?
    SELECT etat INTO etat_exemplaire
    FROM exemplaire
    WHERE id_exemplaire = NEW.id_exemplaire;

    IF etat_exemplaire IS NULL THEN
        RAISE EXCEPTION 'Exemplaire inexistant';
    END IF;

    IF etat_exemplaire <> 'Disponible' THEN
        RAISE EXCEPTION 'Emprunt refusé : exemplaire non disponible';
    END IF;

    -- Quota membre
    SELECT COUNT(*) INTO nb_actuel
    FROM emprunt
    WHERE id_membre = NEW.id_membre
      AND statut IN ('En cours', 'Retard');

    SELECT tm.nb_max_emprunt, tm.duree_max_emprunt
    INTO nb_max, duree
    FROM membre m
    JOIN type_membre tm ON m.id_type_membre = tm.id_type_membre
    WHERE m.id_membre = NEW.id_membre;

    IF nb_actuel >= nb_max THEN
        RAISE EXCEPTION 'Quota maximum atteint (% emprunts)', nb_max;
    END IF;

    -- Dates & statut
    NEW.date_retour_prevue := NEW.date_emprunt + duree;
    NEW.statut := 'En cours';

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;





CREATE OR REPLACE FUNCTION trg_after_insert_emprunt_fn()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE exemplaire
    SET etat = 'Emprunte'
    WHERE id_exemplaire = NEW.id_exemplaire;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;



CREATE OR REPLACE FUNCTION trg_before_update_emprunt_retard_fn()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.statut = 'En cours'
       AND NEW.date_retour_prevue < CURRENT_DATE THEN
        NEW.statut := 'Retard';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;



CREATE OR REPLACE FUNCTION trg_after_update_emprunt_fn()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.statut = 'Termine' AND OLD.statut <> 'Termine' THEN

        UPDATE exemplaire
        SET etat = 'Disponible'
        WHERE id_exemplaire = NEW.id_exemplaire;

        IF NEW.date_retour_effective IS NULL THEN
            UPDATE empruntCREATE OR REPLACE FUNCTION trg_after_update_emprunt_sanction_fn()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.statut = 'Retard' AND NEW.statut = 'Termine' THEN

        INSERT INTO sanction (
            type_sanction,
            montant,
            statut,
            id_membre,
            id_emprunt,
            id_bibliotecaire
        )
        VALUES (
            'Retard',
            500, -- à adapter
            'Non payee',
            NEW.id_membre,
            NEW.id_emprunt,
            NEW.id_bibliotecaire
        );

    END IF;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

            SET date_retour_effective = CURRENT_DATE
            WHERE id_emprunt = NEW.id_emprunt;
        END IF;

    END IF;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;




CREATE OR REPLACE FUNCTION trg_after_update_emprunt_sanction_fn()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.statut = 'Retard' AND NEW.statut = 'Termine' THEN

        INSERT INTO sanction (
            type_sanction,
            montant,
            statut,
            id_membre,
            id_emprunt,
            id_bibliotecaire
        )
        VALUES (
            'Retard',
            500, -- à adapter
            'Non payee',
            NEW.id_membre,
            NEW.id_emprunt,
            NEW.id_bibliotecaire
        );

    END IF;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;



CREATE OR REPLACE FUNCTION trg_before_insert_reservation_fn()
RETURNS TRIGGER AS $$
BEGIN
    IF (SELECT statut_compte FROM membre WHERE id_membre = NEW.id_membre) <> 'Actif' THEN
        RAISE EXCEPTION 'Réservation refusée : membre suspendu';
    END IF;

    NEW.statut := 'En attente';

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

