import pytest
from .conftest import test_client, admin_token, cashier_token

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

def test_get_tables(test_client, cashier_token):
    test_client.post(
        "/tables/",
        headers={"Authorization": f"Bearer {cashier_token}"},
        json={"capacity": 4}
    )

    response = test_client.get(
        "/tables/",
        headers={"Authorization": f"Bearer {cashier_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0

def test_update_table_status(test_client, cashier_token):
    # Crear una mesa
    table_response = test_client.post(
        "/tables/",
        headers={"Authorization": f"Bearer {cashier_token}"},
        json={"capacity": 4}
    )
    table_id = table_response.json()["id"]

    # Actualizar estado
    response = test_client.patch(
        f"/tables/{table_id}/status",
        headers={"Authorization": f"Bearer {cashier_token}"},
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

def test_token_generation(test_client):
    # Registrar usuario
    test_client.post(
        "/auth/register",
        json={
            "username": "testuser2",
            "password": "test123",
            "role": "cashier",
            "is_active": True
        }
    )

    # Obtener token
    response = test_client.post(
        "/auth/token",
        json={
            "username": "testuser2",
            "password": "test123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
