from pydantic import BaseModel, ConfigDict
from datetime import date, datetime
from typing import Optional

# Notifications
class NotificationOut(BaseModel):
    id_notification: int
    message: str
    date_notif: datetime
    lu: bool
    id_membre: int
    model_config = ConfigDict(from_attributes=True)

# Avis
class AvisCreate(BaseModel):
    id_livre: int
    note: int
    commentaire: Optional[str] = None

class AvisOut(AvisCreate):
    id_avis: int
    date_avis: date
    id_membre: int
    model_config = ConfigDict(from_attributes=True)

# Favoris
class FavorisCreate(BaseModel):
    id_livre: int

class FavorisOut(BaseModel):
    id_membre: int
    id_livre: int
    model_config = ConfigDict(from_attributes=True)
