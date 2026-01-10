from pydantic import ConfigDict, BaseModel


class LivreAuteurCreate(BaseModel):
    id_livre: int
    id_auteur: int


class LivreAuteurOut(LivreAuteurCreate):
    model_config = ConfigDict(from_attributes=True)
