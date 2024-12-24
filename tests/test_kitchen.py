import pytest
from datetime import datetime, timedelta
from .conftest import test_client, admin_token, cook_token

def create_test_order(test_client, admin_token):
    """Helper function para crear una orden de prueba"""
    # Crear mesa
    table_response = test_client.post(
        "/tables/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"capacity": 4}
    )
    table_id = table_response.json()["id"]

    # Crear producto
    product_response = test_client.post(
        "/products/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "Test Kitchen Coffee",
            "price": 2.50,
            "category": "Bebidas Calientes",
            "description": "Test description",
            "stock": 100
        }
    )
    product_id = product_response.json()["id"]

    # Crear orden
    order_response = test_client.post(
        "/orders/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "table_id": table_id,
            "items": [
                {
                    "product_id": product_id,
                    "quantity": 1,
                    "notes": "Test note"
                }
            ],
            "notes": "Test order"
        }
    )
    return order_response.json()

def test_get_kitchen_queue(test_client, admin_token, cook_token):
    # Crear algunas órdenes de prueba
    create_test_order(test_client, admin_token)
    create_test_order(test_client, admin_token)

    # Obtener la cola de cocina
    response = test_client.get(
        "/kitchen/orders/queue",
        headers={"Authorization": f"Bearer {cook_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    for order in data:
        assert order["status"] in ["pending", "in_preparation"]

def test_get_next_order(test_client, admin_token, cook_token):
    # Crear una orden de prueba
    create_test_order(test_client, admin_token)

    # Obtener la siguiente orden
    response = test_client.get(
        "/kitchen/orders/next",
        headers={"Authorization": f"Bearer {cook_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "pending"

def test_start_order_preparation(test_client, admin_token, cook_token):
    # Crear una orden
    order = create_test_order(test_client, admin_token)

    # Iniciar preparación
    response = test_client.post(
        f"/kitchen/orders/{order['id']}/start",
        headers={"Authorization": f"Bearer {cook_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "in_preparation"

def test_complete_order(test_client, admin_token, cook_token):
    # Crear una orden
    order = create_test_order(test_client, admin_token)

    # Iniciar preparación
    test_client.post(
        f"/kitchen/orders/{order['id']}/start",
        headers={"Authorization": f"Bearer {cook_token}"}
    )

    # Completar orden
    response = test_client.post(
        f"/kitchen/orders/{order['id']}/complete",
        headers={"Authorization": f"Bearer {cook_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"

def test_get_kitchen_stats(test_client, admin_token, cook_token):
    # Crear algunas órdenes en diferentes estados
    order1 = create_test_order(test_client, admin_token)
    order2 = create_test_order(test_client, admin_token)
    order3 = create_test_order(test_client, admin_token)

    # Iniciar y completar algunas órdenes
    test_client.post(
        f"/kitchen/orders/{order1['id']}/start",
        headers={"Authorization": f"Bearer {cook_token}"}
    )

    test_client.post(
        f"/kitchen/orders/{order2['id']}/start",
        headers={"Authorization": f"Bearer {cook_token}"}
    )
    test_client.post(
        f"/kitchen/orders/{order2['id']}/complete",
        headers={"Authorization": f"Bearer {cook_token}"}
    )

    # Obtener estadísticas
    response = test_client.get(
        "/kitchen/orders/stats",
        headers={"Authorization": f"Bearer {cook_token}"}
    )

    assert response.status_code == 200
    stats = response.json()
    assert "total_orders" in stats
    assert "pending_orders" in stats
    assert "in_preparation" in stats
    assert "completed_orders" in stats
    assert "avg_preparation_time" in stats
    assert stats["total_orders"] >= 3
    assert stats["completed_orders"] >= 1
    assert stats["in_preparation"] >= 1
    assert stats["pending_orders"] >= 1

def test_invalid_order_state_transitions(test_client, admin_token, cook_token):
    # Crear una orden
    order = create_test_order(test_client, admin_token)

    # Intentar completar una orden sin iniciarla
    response = test_client.post(
        f"/kitchen/orders/{order['id']}/complete",
        headers={"Authorization": f"Bearer {cook_token}"}
    )
    assert response.status_code == 400
    assert "no está en preparación" in response.json()["detail"]

    # Iniciar la orden
    test_client.post(
        f"/kitchen/orders/{order['id']}/start",
        headers={"Authorization": f"Bearer {cook_token}"}
    )

    # Intentar iniciar una orden que ya está en preparación
    response = test_client.post(
        f"/kitchen/orders/{order['id']}/start",
        headers={"Authorization": f"Bearer {cook_token}"}
    )
    assert response.status_code == 400
    assert "no está en estado pendiente" in response.json()["detail"]

def test_unauthorized_access(test_client, admin_token):
    # Intentar acceder a la cola de cocina sin ser cocinero
    response = test_client.get(
        "/kitchen/orders/queue",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 403

    # Intentar iniciar una orden sin ser cocinero
    order = create_test_order(test_client, admin_token)
    response = test_client.post(
        f"/kitchen/orders/{order['id']}/start",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 403
