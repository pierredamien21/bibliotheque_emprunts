import os
from sqlalchemy import create_engine, text
from database import engine

def migrate():
    print("Début de la migration de la base de données...")
    
    with engine.connect() as conn:
        # 1. Ajouter image_url à la table livre si absente
        try:
            conn.execute(text("ALTER TABLE livre ADD COLUMN image_url VARCHAR(500)"))
            conn.commit()
            print("Colonne 'image_url' ajoutée à la table 'livre'.")
        except Exception as e:
            if "already exists" in str(e).lower() or "duplicate column" in str(e).lower():
                print("La colonne 'image_url' existe déjà dans 'livre'.")
            else:
                print(f"Erreur lors de l'ajout de image_url : {e}")

        # 2. Créer la table message si absente
        try:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS message (
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
                )
            """))
            conn.commit()
            print("Table 'message' vérifiée/créée.")
        except Exception as e:
            print(f"Erreur lors de la création de la table message : {e}")

        # 3. Rendre id_bibliotecaire optionnel dans reservation (si ce n'est pas déjà le cas)
        try:
            conn.execute(text("ALTER TABLE reservation ALTER COLUMN id_bibliotecaire DROP NOT NULL"))
            conn.commit()
            print("ID Bibliothécaire rendu optionnel dans 'reservation'.")
        except Exception as e:
            print(f"Erreur lors de la modification de reservation : {e}")

    print("Migration terminée !")

if __name__ == "__main__":
    migrate()
