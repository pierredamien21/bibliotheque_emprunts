from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Routers
from routers.auth import router as auth_router
from routers.type_membre import router as type_membre_router
from routers.membre import router as membre_router
from routers.bibliotecaire import router as bibliothecaire_router
from routers.categorie import router as categorie_router
from routers.auteur import router as auteur_router
from routers.livre import router as livre_router
from routers.livre_auteur import router as livre_auteur_router
from routers.exemplaire import router as exemplaire_router
from routers.emprunt import router as emprunt_router
from routers.reservation import router as reservation_router
from routers.sanction import router as sanction_router
from routers.stats import router as stats_router
from routers.notification import router as notification_router
from routers.avis import router as avis_router
from routers.favoris import router as favoris_router

app = FastAPI(
    title="API Gestion Bibliothèque",
    description="API REST pour la gestion des emprunts de livres",
    version="1.0.0"
)

# Configuration CORS pour permettre au frontend de communiquer avec l'API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À restreindre en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# ROUTERS
# =========================
app.include_router(auth_router)
app.include_router(type_membre_router)
app.include_router(membre_router)
app.include_router(bibliothecaire_router)
app.include_router(categorie_router)
app.include_router(auteur_router)
app.include_router(livre_router)
app.include_router(livre_auteur_router)
app.include_router(exemplaire_router)
app.include_router(emprunt_router)
app.include_router(reservation_router)
app.include_router(sanction_router)
app.include_router(stats_router)
app.include_router(notification_router)
app.include_router(avis_router)
app.include_router(favoris_router)

# =========================
# ROOT
# =========================
@app.get("/")
def root():
    return {
        "message": "API Gestion Bibliothèque opérationnelle",
        "docs": "/docs",
        "redoc": "/redoc"
    }
