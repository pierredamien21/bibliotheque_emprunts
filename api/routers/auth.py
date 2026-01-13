from datetime import timedelta, date
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import get_db
from models.models import Bibliothecaire, Membre
from security import (
    verify_password, create_access_token, 
    ACCESS_TOKEN_EXPIRE_MINUTES, get_current_user
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.get("/me")
def get_me(current_user=Depends(get_current_user)):
    """Get the current logged in user information."""
    if isinstance(current_user, Membre):
        return {
            "id": current_user.id_membre,
            "email": current_user.email,
            "nom": current_user.nom,
            "prenom": current_user.prenom,
            "role": "Membre"
        }
    return {
        "id": current_user.id_bibliotecaire,
        "email": current_user.email,
        "login": current_user.login,
        "nom": current_user.nom,
        "prenom": current_user.prenom,
        "role": current_user.role
    }


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Authenticate a bibliothecaire and return a JWT access token.
    
    - **username**: Login of the bibliothecaire
    - **password**: Plain text password
    """
    # Find user by login
    user = db.query(Bibliothecaire).filter(Bibliothecaire.login == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.mot_de_passe_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.login, "role": user.role},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role,
        "nom": user.nom,
        "prenom": user.prenom
    }


@router.post("/login/member")
def login_member(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Authenticate a member and return a JWT access token.
    
    - **username**: email, numero_carte, or login of the member
    - **password**: Plain text password
    """
    # Find member by email, numero_carte, or login
    member = db.query(Membre).filter(
        (Membre.email == form_data.username) | 
        (Membre.numero_carte == form_data.username) | 
        (Membre.login == form_data.username)
    ).first()
    
    if not member or not member.mot_de_passe_hash or not verify_password(form_data.password, member.mot_de_passe_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect identifiers or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if member.statut_compte != "Actif":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is suspended",
        )
    
    # Update last connection
    member.derniere_connexion = date.today()
    db.commit()
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": member.email, "role": "Membre", "id": member.id_membre},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": "Membre",
        "nom": member.nom,
        "prenom": member.prenom,
        "id_membre": member.id_membre
    }
