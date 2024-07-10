from .factories import ParkingFactory, ClientFactory
from parking_app.models import Client, Parking


def test_create_client_with_factories(client, db):
    test_client = ClientFactory()
    db.session.commit()

    assert test_client.id is not None
    assert len(db.session.query(Client).all()) == 2


def test_create_parking_with_factories(client, db):
    test_parking = ParkingFactory()
    db.session.commit()

    assert test_parking.id is not None
    assert len(db.session.query(Parking).all()) == 2
