
import uuid


def test_home(client):
    response = client.get("/")

    assert response.status_code == 200
    assert "API is running successfully" in response.text


def test_create_vehicle(client):
    plate = f"TESTA-{uuid.uuid4().hex[:8]}"

    response = client.post(
        "/vehicles",
        json={
            "license_plate": plate,
            "account_balance": 500,
        },
    )

    assert response.status_code == 201, response.text
    assert response.json()["license_plate"] == plate
    assert response.json()["account_balance"] == 500


def test_duplicate_license_plate(client):
    plate = f"TESTDUP-{uuid.uuid4().hex[:8]}"

    payload = {
        "license_plate": plate,
        "account_balance": 500,
    }

    first_response = client.post("/vehicles", json=payload)
    second_response = client.post("/vehicles", json=payload)

    assert first_response.status_code == 201, first_response.text
    assert second_response.status_code == 409


def test_unknown_vehicle(client):
    response = client.post(
        "/transaction/process",
        json={
            "vehicle_id": 999999,
            "toll_plaza_location": "Test Plaza",
            "toll_fee": 100,
        },
    )

    assert response.status_code == 404


def test_successful_toll_transaction(client):
    create_response = client.post(
        "/vehicles",
        json={
            "license_plate": f"TESTPAY-{uuid.uuid4().hex[:8]}",
            "account_balance": 500,
        },
    )

    assert create_response.status_code == 201, create_response.text
    vehicle_id = create_response.json()["vehicle_id"]

    response = client.post(
        "/transaction/process",
        json={
            "vehicle_id": vehicle_id,
            "toll_plaza_location": "Test Toll Plaza",
            "toll_fee": 100,
        },
    )

    assert response.status_code == 200, response.text

    data = response.json()
    assert data["status"] == "SUCCESS"
    assert data["amount_deducted"] == 100
    assert data["remaining_balance"] == 400
    
    vehicles_response = client.get("/vehicles")
    assert vehicles_response.status_code == 200

    saved_vehicle = next(
        vehicle
        for vehicle in vehicles_response.json()
        if vehicle["id"] == vehicle_id
    )

    assert saved_vehicle["account_balance"] == 400



def test_insufficient_funds_transaction(client):
    create_response = client.post(
        "/vehicles",
        json={
            "license_plate": f"TESTLOW-{uuid.uuid4().hex[:8]}",
            "account_balance": 50,
        },
    )

    assert create_response.status_code == 201, create_response.text
    vehicle_id = create_response.json()["vehicle_id"]

    response = client.post(
        "/transaction/process",
        json={
            "vehicle_id": vehicle_id,
            "toll_plaza_location": "Test Toll Plaza",
            "toll_fee": 100,
        },
    )

    assert response.status_code == 200, response.text

    data = response.json()
    assert data["status"] == "INSUFFICIENT_FUNDS"
    assert data["amount_deducted"] == 0
    assert data["remaining_balance"] == 50
    
    vehicles_response = client.get("/vehicles")
    assert vehicles_response.status_code == 200

    saved_vehicle = next(
        vehicle
        for vehicle in vehicles_response.json()
        if vehicle["id"] == vehicle_id
    )

    assert saved_vehicle["account_balance"] == 50


def test_analytics_summary(client):
    plate = f"TESTA-{uuid.uuid4().hex[:8]}"

    create_response = client.post(
        "/vehicles",
        json={
            "license_plate": plate,
            "account_balance": 500,
        },
    )

    assert create_response.status_code == 201, create_response.text
    vehicle_id = create_response.json()["vehicle_id"]

    # Successful transaction: ₹100
    success_response = client.post(
        "/transaction/process",
        json={
            "vehicle_id": vehicle_id,
            "toll_plaza_location": "Analytics Test Plaza",
            "toll_fee": 100,
        },
    )
    assert success_response.status_code == 200

    # Failed transaction: insufficient funds
    failed_response = client.post(
        "/transaction/process",
        json={
            "vehicle_id": vehicle_id,
            "toll_plaza_location": "Analytics Test Plaza",
            "toll_fee": 1000,
        },
    )
    assert failed_response.status_code == 200

    # Check analytics
    response = client.get("/analytics/summary")
    assert response.status_code == 200

    data = response.json()
    assert data["total_transactions"] == 2
    assert data["successful_transactions"] == 1
    assert data["insufficient_funds_transactions"] == 1
    assert data["total_revenue_collected"] == 100
