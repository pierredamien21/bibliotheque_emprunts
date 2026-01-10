import sys
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Add api directory to sys.path so 'routers' can be imported by main.py
sys.path.append(os.path.join(os.getcwd(), "api"))

# Important: Import database directly as routers do, to ensure dependency override works on the same function object
from database import Base, get_db
from main import app

# Use in-memory SQLite for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a TestClient with overridden database dependency."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
from security import create_access_token
from models.models import Bibliothecaire

@pytest.fixture(scope="function")
def authorized_client(client, db_session):
    """Create a TestClient with a valid Bearer token."""
    # 1. Create a user in the DB
    user = Bibliothecaire(
        matricule="TEST-ADMIN",
        nom="Admin",
        prenom="Test",
        email="admin.test@example.com",
        login="admin_test",
        mot_de_passe_hash="hashed_secret",
        role="Admin"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # 2. PROPERLY generate token using the user's login
    token = create_access_token(data={"sub": user.login, "role": user.role})
    
    # 3. Add header
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }
    return client


@pytest.fixture(scope="function")
def member_client(client, db_session):
    """Create a TestClient authenticated as a regular member."""
    from models.models import Membre, TypeMembre
    from security import hash_password

    # 1. Create a TypeMembre if not exists
    tm = db_session.query(TypeMembre).first()
    if not tm:
        tm = TypeMembre(nom_type="Etudiant", duree_max_emprunt=14, nb_max_emprunt=5)
        db_session.add(tm)
        db_session.commit()
    
    # 2. Create a member
    member = Membre(
        numero_carte="TEST-MEM-001",
        nom="User",
        prenom="Test",
        email="member.test@example.com",
        login="member_test",
        mot_de_passe_hash=hash_password("password123"),
        statut_compte="Actif",
        id_type_membre=tm.id_type_membre
    )
    db_session.add(member)
    db_session.commit()
    db_session.refresh(member)

    # 3. Generate token for the member
    token = create_access_token(data={"sub": member.email, "role": "Membre", "id": member.id_membre})
    
    # 4. Add header
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }
    return client
