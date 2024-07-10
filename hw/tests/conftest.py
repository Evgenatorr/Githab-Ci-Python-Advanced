import pytest
from datetime import datetime
from flask import template_rendered
from parking_app.my_app import create_app
from parking_app.models import Client, Parking, ClientParking, db as _db
from parking_app.config import TestConfig


@pytest.fixture
def app():
    _app = create_app(config=TestConfig)

    with _app.app_context():
        _db.create_all()

        test_client = Client(
            name="name",
            surname="surname",
            credit_card='1231234',
            car_number='3asd123'
        )
        test_parking = Parking(
            address="Puskina",
            count_places=2,
            count_available_places=2
        )
        test_client_parking = ClientParking(
            client_id=1,
            parking_id=1,
            time_in=datetime.now(),
            time_out=datetime.now()
        )

        _db.session.add(test_client)
        _db.session.add(test_parking)
        _db.session.add(test_client_parking)
        _db.session.commit()

        yield _app

        _db.session.close()
        _db.drop_all()



@pytest.fixture
def client(app):
    client = app.test_client()
    yield client


@pytest.fixture
def captured_templates(app):
    recorded = []

    def record(sender, template, context, **extra):
        recorded.append((template, context))

    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)


@pytest.fixture
def db(app):
    with app.app_context():
        yield _db
