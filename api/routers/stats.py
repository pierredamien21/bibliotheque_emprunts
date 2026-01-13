from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.models import Livre, Membre, Emprunt, Exemplaire, Bibliothecaire, Categorie
from sqlalchemy import func
from security import get_current_staff

router = APIRouter(prefix="/stats", tags=["Statistics"])

@router.get("/")
def get_stats(db: Session = Depends(get_db), current_user: Bibliothecaire = Depends(get_current_staff)):
    """Get global library statistics (Staff only)."""
    # 0. Comptages Globaux
    total_livres = db.query(Livre).count()
    total_membres = db.query(Membre).count()
    total_exemplaires = db.query(Exemplaire).count()
    emprunts_actifs = db.query(Emprunt).filter(Emprunt.statut.in_(["En cours", "Retard"])).count()
    retards = db.query(Emprunt).filter(Emprunt.statut == "Retard").count()

    # Analytics Avancés
    # 1. Top 5 livres les plus empruntés
    top_livres = db.query(
        Livre.titre, 
        func.count(Emprunt.id_emprunt).label("total")
    ).join(Exemplaire, Livre.id_livre == Exemplaire.id_livre)\
     .join(Emprunt, Exemplaire.id_exemplaire == Emprunt.id_exemplaire)\
     .group_by(Livre.id_livre, Livre.titre)\
     .order_by(func.count(Emprunt.id_emprunt).desc())\
     .limit(5).all()

    # 2. Livre par catégorie
    cat_stats = db.query(
        Categorie.nom_categorie,
        func.count(Livre.id_livre).label("nb_livres")
    ).join(Livre, Categorie.id_categorie == Livre.id_categorie)\
     .group_by(Categorie.id_categorie, Categorie.nom_categorie).all()

    return {
        "global": {
            "total_livres": total_livres,
            "total_membres": total_membres,
            "total_exemplaires": total_exemplaires,
            "emprunts_actifs": emprunts_actifs,
            "retards": retards
        },
        "top_livres": [{"titre": t[0], "emprunts": t[1]} for t in top_livres],
        "par_categorie": [{"categorie": c[0], "nombre": c[1]} for c in cat_stats]
    }
