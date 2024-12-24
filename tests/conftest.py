import sys
import os
from typing import Generator

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db

# Configuración de la base de datos de prueba
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Sobreescribir la dependencia de la base de datos
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
def test_client():
    client = TestClient(app)
    return client

@pytest.fixture
def admin_token(test_client):
    # Crear usuario admin
    response = test_client.post(
        "/auth/register",
        json={
            "username": "admin",
            "password": "admin123",
            "role": "admin",
            "is_active": True
        }
    )
    assert response.status_code == 201

    # Obtener token
    response = test_client.post(
        "/auth/token",
        json={
            "username": "admin",
            "password": "admin123"
        }
    )
    assert response.status_code == 200
    return response.json()["access_token"]

@pytest.fixture
def cook_token(test_client):
    # Crear usuario cocinero
    response = test_client.post(
        "/auth/register",
        json={
            "username": "cook1",
            "password": "cook123",
            "role": "cook",
            "is_active": True
        }
    )
    assert response.status_code == 201

    # Obtener token
    response = test_client.post(
        "/auth/token",
        json={
            "username": "cook1",
            "password": "cook123"
        }
    )
    assert response.status_code == 200
    return response.json()["access_token"]

@pytest.fixture
def cashier_token(test_client):
    # Crear usuario cajero
    response = test_client.post(
        "/auth/register",
        json={
            "username": "cashier1",
            "password": "cash123",
            "role": "cashier",
            "is_active": True
        }
    )
    assert response.status_code == 201

    # Obtener token
    response = test_client.post(
        "/auth/token",
        json={
            "username": "cashier1",
            "password": "cash123"
        }
    )
    assert response.status_code == 200
    return response.json()["access_token"]
