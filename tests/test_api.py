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
from app.models import User, Table, Product

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

def test_create_user(test_client):
    response = test_client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "password": "test123",
            "role": "cashier",
            "is_active": True
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "testuser"
    assert data["role"] == "cashier"

def test_create_table(test_client, admin_token):
    response = test_client.post(
        "/tables/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"capacity": 4}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["capacity"] == 4
    assert data["status"] == "free"

def test_create_product(test_client, admin_token):
    response = test_client.post(
        "/products/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "Test Coffee",
            "price": 2.50,
            "category": "Bebidas Calientes",
            "description": "Test description",
            "stock": 100
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Coffee"
    assert float(data["price"]) == 2.50

def test_get_tables(test_client, admin_token):
    # Crear una mesa primero
    test_client.post(
        "/tables/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"capacity": 4}
    )

    response = test_client.get(
        "/tables/",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0

def test_update_table_status(test_client, admin_token):
    # Crear una mesa
    table_response = test_client.post(
        "/tables/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"capacity": 4}
    )
    table_id = table_response.json()["id"]

    # Actualizar estado
    response = test_client.patch(
        f"/tables/{table_id}/status",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"status": "occupied"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "occupied"

def test_get_products_by_category(test_client, admin_token):
    # Crear productos
    test_client.post(
        "/products/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "Test Coffee",
            "price": 2.50,
            "category": "Bebidas Calientes",
            "description": "Test description",
            "stock": 100
        }
    )

    response = test_client.get(
        "/products/?category=Bebidas+Calientes",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert all(p["category"] == "Bebidas Calientes" for p in data)
