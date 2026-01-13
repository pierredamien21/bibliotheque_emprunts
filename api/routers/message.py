from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from database import get_db
from models.models import Message, Bibliothecaire, Membre
from schemas.v3_schemas import MessageCreate, MessageOut, MessageReply
from security import get_current_user, get_current_staff

router = APIRouter(prefix="/messages", tags=["Messages"])

@router.post("/", response_model=MessageOut)
def send_message(data: MessageCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    if not isinstance(current_user, Membre):
        raise HTTPException(403, "Seuls les membres peuvent envoyer des messages initiaux.")
    
    msg = Message(
        id_membre=current_user.id_membre,
        contenu=data.contenu,
        statut="Envoye"
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg

@router.get("/", response_model=list[MessageOut])
def get_messages(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    if isinstance(current_user, Bibliothecaire):
        # Staff sees everything
        return db.query(Message).all()
    # Members see only their messages
    return db.query(Message).filter(Message.id_membre == current_user.id_membre).all()

@router.patch("/{id_message}/repondre", response_model=MessageOut)
def reply_message(id_message: int, data: MessageReply, db: Session = Depends(get_db), current_user: Bibliothecaire = Depends(get_current_staff)):
    msg = db.get(Message, id_message)
    if not msg:
        raise HTTPException(404, "Message introuvable")
    
    msg.id_bibliotecaire = current_user.id_bibliotecaire
    msg.reponse = data.reponse
    msg.date_reponse = datetime.utcnow()
    msg.statut = "Repondu"
    
    db.commit()
    db.refresh(msg)
    return msg
