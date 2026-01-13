from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from database import get_db
from models.models import Livre, Exemplaire, Bibliothecaire, Categorie, Emprunt, Membre, Avis
from schemas.livre import LivreCreate, LivreOut
from security import get_current_staff, get_current_user

router = APIRouter(prefix="/livres", tags=["Livres"])


@router.get("/", response_model=list[LivreOut])
def get_all(
    titre: Optional[str] = None, 
    id_categorie: Optional[int] = None, 
    db: Session = Depends(get_db)
):
    query = db.query(Livre)
    if titre:
        query = query.filter(Livre.titre.ilike(f"%{titre}%"))
    if id_categorie:
        query = query.filter(Livre.id_categorie == id_categorie)
    
    livres = query.all()
    
    # Calculate availability for each book
    result = []
    for livre in livres:
        nb_dispo = db.query(Exemplaire).filter(
            Exemplaire.id_livre == livre.id_livre,
            Exemplaire.etat == "Disponible",
            Exemplaire.statut_logique == "Actif"
        ).count()
        
        # We need to add nb_disponible to the object for Pydantic to pick it up
        livre_dict = {c.name: getattr(livre, c.name) for c in livre.__table__.columns}
        livre_dict["nb_disponible"] = nb_dispo
        result.append(livre_dict)
        
    return result


@router.post("/", response_model=LivreOut)
def create(data: LivreCreate, db: Session = Depends(get_db), current_user: Bibliothecaire = Depends(get_current_staff)):
    obj = Livre(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/recommandations", response_model=list[LivreOut])
def get_recommendations(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """
    Algorithme hybride de recommandation :
    1. Identifie les catégories préférées de l'utilisateur.
    2. Exclut les livres déjà lus.
    3. Complète avec les livres les mieux notés ou récents (Cold Start).
    """
    if not isinstance(current_user, Membre):
        # Staff : Retourne simplement les livres les plus récents
        return db.query(Livre).order_by(desc(Livre.date_ajout_catalogue)).limit(5).all()

    # 1. Trouver les catégories préférées (Top 3) via les emprunts
    pref_categories = db.query(Livre.id_categorie, func.count(Emprunt.id_emprunt).label("cnt"))\
        .join(Emprunt, Emprunt.id_exemplaire == Livre.id_livre)\
        .filter(Emprunt.id_membre == current_user.id_membre)\
        .group_by(Livre.id_categorie)\
        .order_by(desc("cnt"))\
        .limit(3).all()
    
    category_ids = [c[0] for c in pref_categories]

    # 2. Identifier les livres déjà empruntés pour les exclure
    empruntes_ids = db.query(Emprunt.id_exemplaire)\
        .filter(Emprunt.id_membre == current_user.id_membre).all()
    exclude_ids = [e[0] for e in empruntes_ids]

    # 3. Rechercher des recommandations
    recommendations = []
    
    if category_ids:
        # Suggestions dans ses catégories préférées
        recommendations = db.query(Livre)\
            .filter(Livre.id_categorie.in_(category_ids))\
            .filter(~Livre.id_livre.in_(exclude_ids))\
            .order_by(func.random())\
            .limit(5).all()

    # 4. Si pas assez de recommandations, ajouter les livres les mieux notés
    if len(recommendations) < 5:
        sub_exclude = exclude_ids + [r.id_livre for r in recommendations]
        top_rated = db.query(Livre)\
            .join(Avis, Avis.id_livre == Livre.id_livre)\
            .filter(~Livre.id_livre.in_(sub_exclude))\
            .group_by(Livre.id_livre)\
            .order_by(desc(func.avg(Avis.note)))\
            .limit(5 - len(recommendations)).all()
        recommendations.extend(top_rated)

    # 5. Si toujours pas assez, prendre les plus récents
    if len(recommendations) < 5:
        sub_exclude_2 = exclude_ids + [r.id_livre for r in recommendations]
        recent = db.query(Livre)\
            .filter(~Livre.id_livre.in_(sub_exclude_2))\
            .order_by(desc(Livre.date_ajout_catalogue))\
            .limit(5 - len(recommendations)).all()
        recommendations.extend(recent)

    return recommendations


@router.get("/{id_livre}", response_model=LivreOut)
def get_one(id_livre: int, db: Session = Depends(get_db)):
    obj = db.get(Livre, id_livre)
    if not obj:
        raise HTTPException(404, "Livre introuvable")
    return obj


@router.put("/{id_livre}", response_model=LivreOut)
def update(id_livre: int, data: LivreCreate, db: Session = Depends(get_db), current_user: Bibliothecaire = Depends(get_current_staff)):
    obj = db.get(Livre, id_livre)
    if not obj:
        raise HTTPException(404, "Livre introuvable")
    for key, value in data.model_dump().items():
        setattr(obj, key, value)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{id_livre}")
def delete(id_livre: int, db: Session = Depends(get_db), current_user: Bibliothecaire = Depends(get_current_staff)):
    obj = db.get(Livre, id_livre)
    if not obj:
        raise HTTPException(404, "Livre introuvable")
    db.delete(obj)
    db.commit()
    return {"message": "Livre supprimé avec succès"}
