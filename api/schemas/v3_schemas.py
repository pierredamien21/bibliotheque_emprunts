from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class MessageCreate(BaseModel):
    contenu: str = Field(..., description="Contenu de la question ou du message")

class MessageReply(BaseModel):
    reponse: str = Field(..., description="Réponse du bibliothécaire")

class MessageOut(BaseModel):
    id_message: int
    id_membre: int
    id_bibliotecaire: Optional[int]
    contenu: str
    reponse: Optional[str]
    date_envoi: datetime
    date_reponse: Optional[datetime]
    statut: str

    class Config:
        from_attributes = True
