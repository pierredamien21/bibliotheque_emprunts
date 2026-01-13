from sqlalchemy import (
    Column, Integer, String, Date, ForeignKey, Text, Numeric, Boolean, DateTime
)
from sqlalchemy.sql import func
from database import Base
from datetime import date


# =========================
# TYPE MEMBRE
# =========================
class TypeMembre(Base):
    __tablename__ = "type_membre"

    id_type_membre = Column(Integer, primary_key=True, index=True)
    nom_type = Column(String(50), nullable=False)
    duree_max_emprunt = Column(Integer, nullable=False)
    nb_max_emprunt = Column(Integer, nullable=False)


# =========================
# MEMBRE
# =========================
class Membre(Base):
    __tablename__ = "membre"

    id_membre = Column(Integer, primary_key=True, index=True)
    numero_carte = Column(String(30), unique=True, nullable=False)
    nom = Column(String(100), nullable=False)
    prenom = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    telephone = Column(String(30))
    adresse = Column(Text)
    date_naissance = Column(Date)
    date_inscription = Column(Date, default=date.today)
    statut_compte = Column(String(20), nullable=False)
    login = Column(String(50), unique=True)
    mot_de_passe_hash = Column(Text)
    derniere_connexion = Column(Date) # Note: using Date for simplicity as per existing pattern, but TIMESTAMP/Datetime would be better. SQLAlchemy Date handles date objects.

    id_type_membre = Column(Integer, ForeignKey("type_membre.id_type_membre"), nullable=False)


# =========================
# BIBLIOTHECAIRE
# =========================
class Bibliothecaire(Base):
    __tablename__ = "bibliothecaire"

    id_bibliotecaire = Column(Integer, primary_key=True, index=True)
    matricule = Column(String(30), unique=True, nullable=False)
    nom = Column(String(100), nullable=False)
    prenom = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    telephone = Column(String(30))
    login = Column(String(50), unique=True, nullable=False)
    mot_de_passe_hash = Column(Text, nullable=False)
    role = Column(String(20), nullable=False)


# =========================
# CATEGORIE
# =========================
class Categorie(Base):
    __tablename__ = "categorie"

    id_categorie = Column(Integer, primary_key=True, index=True)
    nom_categorie = Column(String(100), nullable=False)
    description = Column(Text)


# =========================
# AUTEUR
# =========================
class Auteur(Base):
    __tablename__ = "auteur"

    id_auteur = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100), nullable=False)
    prenom = Column(String(100), nullable=False)


# =========================
# LIVRE
# =========================
class Livre(Base):
    __tablename__ = "livre"

    id_livre = Column(Integer, primary_key=True, index=True)
    titre = Column(String(200), nullable=False)
    descriptions = Column(Text)
    isbn = Column(String(30), unique=True)
    editeur = Column(String(150))
    langue = Column(String(50))
    annee_publication = Column(Integer)
    date_ajout_catalogue = Column(Date, default=date.today)

    id_categorie = Column(Integer, ForeignKey("categorie.id_categorie"), nullable=False)
    image_url = Column(String(500)) # URL vers la couverture du livre


# =========================
# EXEMPLAIRE
# =========================
class Exemplaire(Base):
    __tablename__ = "exemplaire"

    id_exemplaire = Column(Integer, primary_key=True, index=True)
    code_barre = Column(String(50), unique=True, nullable=False)
    etat = Column(String(20), nullable=False)
    statut_logique = Column(String(20), nullable=False)
    date_acquisition = Column(Date, default=date.today)
    localisation = Column(String(100))

    id_livre = Column(Integer, ForeignKey("livre.id_livre"), nullable=False)


# =========================
# EMPRUNT
# =========================
class Emprunt(Base):
    __tablename__ = "emprunt"

    id_emprunt = Column(Integer, primary_key=True, index=True)
    date_emprunt = Column(Date, default=date.today)
    date_retour_prevue = Column(Date)
    date_retour_effective = Column(Date)
    statut = Column(String(20), nullable=False)
    renouvellement_count = Column(Integer, nullable=False, default=0)
    commentaire = Column(Text)

    id_membre = Column(Integer, ForeignKey("membre.id_membre"), nullable=False)
    id_exemplaire = Column(Integer, ForeignKey("exemplaire.id_exemplaire"), nullable=False)
    id_bibliotecaire = Column(Integer, ForeignKey("bibliothecaire.id_bibliotecaire"), nullable=False)


# =========================
# RESERVATION
# =========================
class Reservation(Base):
    __tablename__ = "reservation"

    id_reservation = Column(Integer, primary_key=True, index=True)
    date_reservation = Column(Date, default=date.today)
    statut = Column(String(20), nullable=False)
    priorite = Column(Integer, nullable=False)

    id_membre = Column(Integer, ForeignKey("membre.id_membre"), nullable=False)
    id_livre = Column(Integer, ForeignKey("livre.id_livre"), nullable=False)
    id_bibliotecaire = Column(Integer, ForeignKey("bibliothecaire.id_bibliotecaire"), nullable=True)


# =========================
# SANCTION
# =========================
class Sanction(Base):
    __tablename__ = "sanction"

    id_sanction = Column(Integer, primary_key=True, index=True)
    type_sanction = Column(String(30), nullable=False)
    montant = Column(Numeric(10, 2))
    date_sanction = Column(Date, default=date.today)
    date_fin_suspension = Column(Date)
    statut = Column(String(20), nullable=False)

    id_membre = Column(Integer, ForeignKey("membre.id_membre"), nullable=False)
    id_emprunt = Column(Integer, ForeignKey("emprunt.id_emprunt"), nullable=False)
    id_bibliotecaire = Column(Integer, ForeignKey("bibliothecaire.id_bibliotecaire"), nullable=False)




class LivreAuteur(Base):
    __tablename__ = "livre_auteur"

    id_livre = Column(Integer, ForeignKey("livre.id_livre", ondelete="CASCADE"), primary_key=True)
    id_auteur = Column(Integer, ForeignKey("auteur.id_auteur", ondelete="CASCADE"), primary_key=True)


# =========================
# AVIS
# =========================
class Avis(Base):
    __tablename__ = "avis"

    id_avis = Column(Integer, primary_key=True, index=True)
    note = Column(Integer, nullable=False)
    commentaire = Column(Text)
    date_avis = Column(Date, default=date.today)
    
    id_membre = Column(Integer, ForeignKey("membre.id_membre", ondelete="CASCADE"), nullable=False)
    id_livre = Column(Integer, ForeignKey("livre.id_livre", ondelete="CASCADE"), nullable=False)


# =========================
# FAVORIS
# =========================
class Favoris(Base):
    __tablename__ = "favoris"

    id_membre = Column(Integer, ForeignKey("membre.id_membre", ondelete="CASCADE"), primary_key=True)
    id_livre = Column(Integer, ForeignKey("livre.id_livre", ondelete="CASCADE"), primary_key=True)


# =========================
# NOTIFICATION
# =========================
class Notification(Base):
    __tablename__ = "notification"

    id_notification = Column(Integer, primary_key=True, index=True)
    message = Column(Text, nullable=False)
    date_notif = Column(DateTime, default=func.now())
    lu = Column(Boolean, default=False)
    
    id_membre = Column(Integer, ForeignKey("membre.id_membre", ondelete="CASCADE"), nullable=False)
