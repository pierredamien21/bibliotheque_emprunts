from pydantic import ConfigDict, BaseModel


class AuteurBase(BaseModel):
    nom: str
    prenom: str


class AuteurCreate(AuteurBase):
    pass


class AuteurOut(AuteurBase):
    id_auteur: int

    model_config = ConfigDict(from_attributes=True)
