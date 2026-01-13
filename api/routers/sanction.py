from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.models import Sanction
from schemas.sanction import SanctionCreate, SanctionOut
from security import get_current_staff, get_current_user
from models.models import Bibliothecaire, Membre

router = APIRouter(prefix="/sanctions", tags=["Sanctions"])


@router.get("/mes-sanctions", response_model=list[SanctionOut])
def get_mes_sanctions(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    if not isinstance(current_user, Membre):
        from fastapi import HTTPException
        raise HTTPException(403, "Seuls les membres peuvent accéder à leurs sanctions via ce raccourci.")
    return db.query(Sanction).filter(Sanction.id_membre == current_user.id_membre).all()


@router.get("/", response_model=list[SanctionOut])
def get_all(db: Session = Depends(get_db), current_user: Bibliothecaire = Depends(get_current_staff)):
    return db.query(Sanction).all()


@router.post("/", response_model=SanctionOut)
def create(data: SanctionCreate, db: Session = Depends(get_db), current_user: Bibliothecaire = Depends(get_current_staff)):
    obj = Sanction(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/{id_sanction}", response_model=SanctionOut)
def get_one(id_sanction: int, db: Session = Depends(get_db), current_user: Bibliothecaire = Depends(get_current_staff)):
    from fastapi import HTTPException
    obj = db.get(Sanction, id_sanction)
    if not obj:
        raise HTTPException(404, "Sanction introuvable")
    return obj


@router.patch("/{id_sanction}/statut")
def update_statut(id_sanction: int, statut: str, db: Session = Depends(get_db), current_user: Bibliothecaire = Depends(get_current_staff)):
    from fastapi import HTTPException
    if statut not in ["Payee", "Non payee"]:
        raise HTTPException(400, "Statut invalide. Valeurs: 'Payee', 'Non payee'")
    obj = db.get(Sanction, id_sanction)
    if not obj:
        raise HTTPException(404, "Sanction introuvable")
    obj.statut = statut
    db.commit()
    return {"message": f"Statut mis à jour: {statut}"}
