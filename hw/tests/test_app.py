import pytest
from datetime import datetime
from parking_app.models import Parking, ClientParking


@pytest.mark.parametrize(
    "route", ["/clients", "/clients/1", "/parkings", "/parkings/1"]
)
def test_route_status(client, route):
    response = client.get(route)
    assert response.status_code == 200


def test_create_client(client):
    client_data = {
        "name": "name",
        "surname": "surname",
        "credit_card": "1234",
        "car_number": "3zxc443",
    }
    response = client.post("/clients", json=client_data)
    assert response.status_code == 201
    assert response.json["id"] == 2


def test_create_parking(client):
    parking_data = {
        "address": "address",
        "count_places": 1,
        "count_available_places": 1,
    }
    response = client.post("/parkings", json=parking_data)
    assert response.status_code == 201
    assert response.json["id"] == 2

    # Проверяем что парковка с таким же адресом не может быть создана
    response = client.post("/parkings", json=parking_data)
    assert response.status_code == 400


@pytest.mark.parking_entrance
def test_parking_entrance(client, db):

    client_parking_data = {"client_id": 1, "parking_id": 1}
    parking = db.session.query(Parking).filter(Parking.id == 1).first()
    assert parking.count_available_places == 2

    response = client.post("/client_parkings", json=client_parking_data)
    assert response.status_code == 201
    assert response.json["id"] == 1

    # Проверяем что количество мест на парковке 1 уменьшилось
    assert parking.count_available_places == 1

    # Проверяем что ещё одной такой же связки
    # client_id и parking_id быть не может
    response = client.post("/client_parkings", json=client_parking_data)
    assert response.status_code == 400


@pytest.mark.exit_parking
def test_exit_from_parking(client, db):

    client_parking_data = {"client_id": 1, "parking_id": 1}

    client_parking = (
        db.session.query(ClientParking).filter(ClientParking.id == 1).first()
    )
    client_parking.time_out = None

    parking = db.session.query(Parking).filter(Parking.id == 1).first()
    assert parking.count_available_places == 2

    response = client.delete("/client_parkings", json=client_parking_data)
    assert response.status_code == 201

    # Проверяем что количество мест на парковке 1 увеличилось
    assert parking.count_available_places == 3

    # Проверяем что клиент, находящийся на парковке не может заехать ещё раз
    client_parking.time_out = datetime.now()
    response = client.delete("/client_parkings", json=client_parking_data)
    assert response.status_code == 400
