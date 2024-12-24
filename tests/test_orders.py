import pytest
from .conftest import test_client, admin_token, cook_token, cashier_token

def test_create_order(test_client, admin_token):
    # Primero crear una mesa
    table_response = test_client.post(
        "/tables/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"capacity": 4}
    )
    assert table_response.status_code == 201
    table_id = table_response.json()["id"]

    # Crear un producto
    product_response = test_client.post(
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
    assert product_response.status_code == 201
    product_id = product_response.json()["id"]

    # Crear la orden
    response = test_client.post(
        "/orders/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "table_id": table_id,
            "items": [
                {
                    "product_id": product_id,
                    "quantity": 2,
                    "notes": "Sin azúcar"
                }
            ],
            "notes": "Orden de prueba"
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert data["table_id"] == table_id
    assert len(data["items"]) == 1
    assert data["items"][0]["product_id"] == product_id
    assert data["items"][0]["quantity"] == 2
    assert data["status"] == "pending"

def test_get_orders(test_client, admin_token):
    response = test_client.get(
        "/orders/",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_get_kitchen_orders(test_client, cook_token, admin_token):
    # Primero crear orden con admin_token
    table_response = test_client.post(
        "/tables/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"capacity": 4}
    )
    table_id = table_response.json()["id"]

    product_response = test_client.post(
        "/products/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "Test Coffee 2",
            "price": 2.50,
            "category": "Bebidas Calientes",
            "description": "Test description",
            "stock": 100
        }
    )
    product_id = product_response.json()["id"]

    # Crear orden como admin
    test_client.post(
        "/orders/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "table_id": table_id,
            "items": [
                {
                    "product_id": product_id,
                    "quantity": 1
                }
            ]
        }
    )

    # Consultar como cocinero
    response = test_client.get(
        "/orders/kitchen/pending",
        headers={"Authorization": f"Bearer {cook_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert all(order["status"] in ["pending", "in_preparation"] for order in data)

def test_update_order_status(test_client, cook_token, admin_token):
    # Crear orden como admin
    table_response = test_client.post(
        "/tables/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"capacity": 4}
    )
    table_id = table_response.json()["id"]

    product_response = test_client.post(
        "/products/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "Test Coffee 3",
            "price": 2.50,
            "category": "Bebidas Calientes",
            "description": "Test description",
            "stock": 100
        }
    )
    product_id = product_response.json()["id"]

    order_response = test_client.post(
        "/orders/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "table_id": table_id,
            "items": [
                {
                    "product_id": product_id,
                    "quantity": 1
                }
            ]
        }
    )
    order_id = order_response.json()["id"]

    # Actualizar estado como cocinero
    response = test_client.patch(
        f"/orders/{order_id}",
        headers={"Authorization": f"Bearer {cook_token}"},
        json={
            "status": "in_preparation",
            "notes": "En preparación"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "in_preparation"
    assert data["notes"] == "En preparación"

def test_create_order_invalid_table(test_client, cashier_token):
    response = test_client.post(
        "/orders/",
        headers={"Authorization": f"Bearer {cashier_token}"},
        json={
            "table_id": 999999,  # ID inexistente
            "items": [
                {
                    "product_id": 1,
                    "quantity": 1
                }
            ]
        }
    )
    assert response.status_code == 404
    assert "Mesa no encontrada" in response.json()["detail"]
