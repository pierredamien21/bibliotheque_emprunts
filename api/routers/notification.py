from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.models import Notification, Membre
from schemas.v2_schemas import NotificationOut
from security import get_current_user

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get("/", response_model=list[NotificationOut])
def get_my_notifications(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    if isinstance(current_user, Membre):
        return db.query(Notification).filter(Notification.id_membre == current_user.id_membre).order_by(Notification.date_notif.desc()).all()
    # Staff see all
    return db.query(Notification).order_by(Notification.date_notif.desc()).all()

@router.patch("/{id_notification}/lu")
def mark_as_read(id_notification: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    notif = db.get(Notification, id_notification)
    if not notif:
        raise HTTPException(404, "Notification introuvable")
    
    if isinstance(current_user, Membre) and notif.id_membre != current_user.id_membre:
        raise HTTPException(403, "Accès refusé")
        
    notif.lu = True
    db.commit()
    return {"message": "Notification marquée comme lue"}
