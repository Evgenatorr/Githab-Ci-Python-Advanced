from flask import Flask

from .models import db, Client, ClientParking, Parking
from datetime import datetime

from flask import jsonify, request
from sqlalchemy.exc import NoResultFound, IntegrityError

from .schemas import (ClientSchema,
                      ParkingSchema,
                      ClientParkingSchema,
                      ValidationError)


def create_app(config) -> Flask:
    """
    Создаем приложение Flask
    """

    app = Flask(__name__)
    app.config.from_object(config)
    db.init_app(app)

    @app.before_request
    def before_request_func():
        db.create_all()

    @app.route("/clients", methods=["GET"])
    def get_clients():
        """
        Список всех клиентов
        """

        client_schema = ClientSchema()
        clients = db.session.query(Client).all()

        if len(clients) < 1:
            return jsonify(ClientsNotFound="Clients not found"), 404

        return client_schema.dump(clients, many=True)

    @app.route("/clients/<int:client_id>", methods=["GET"])
    def get_client_by_id(client_id: int):
        """
        Клиент по id
        """

        client_schema = ClientSchema()
        client = (db.session.query(Client)
                  .filter(Client.id == client_id)
                  .one_or_none())

        if client is None:
            return jsonify(
                ClientNotFound=
                "Client with this id not found"
            ), 404

        return client_schema.dump(client), 200

    @app.route("/clients", methods=["POST"])
    def create_client():
        """
        Создать клиента

        body:

        {
        "name": "Vasya",
        "surname": "Pupkov",
        "credit_card": "123",
        "car_number": "123"
        }
        """

        client_schema = ClientSchema()
        data = request.json

        try:
            client = client_schema.load(data)

        except ValidationError as exc:
            return exc.messages, 400

        db.session.add(client)
        db.session.commit()

        return client_schema.dump(client), 201

    @app.route("/parkings", methods=["GET"])
    def get_parkings():
        """
        Список всех парковок
        """

        parking_schema = ParkingSchema()
        parkings = db.session.query(Parking).all()

        if len(parkings) < 1:
            return jsonify(
                ParkingsNotFound="Parkings not found"
            ), 404

        return parking_schema.dump(parkings, many=True)

    @app.route("/parkings/<int:parking_id>", methods=["GET"])
    def get_parkings_by_id(parking_id: int):
        """
        Вывод парковки по id
        """

        parking_schema = ParkingSchema()
        parking = (
            db.session.query(Parking).filter(Parking.id == parking_id)
            .one_or_none()
        )

        if parking is None:
            return jsonify(
                ParkingNotFound="Parking with this id not found"
            ), 404

        return parking_schema.dump(parking)

    @app.route("/parkings", methods=["POST"])
    def create_parking():
        """
        Создать парковку

        body:

        {
        "address": "Puskina",
        "count_places": 2,
        "count_available_places": 2
        }
        """

        parking_schema = ParkingSchema()
        data = request.json

        try:
            parking = parking_schema.load(data)

        except ValidationError as exc:
            return exc.messages, 400

        try:
            db.session.add(parking)
            db.session.commit()

        except IntegrityError:
            return jsonify(error="such address already exists"), 400

        return parking_schema.dump(parking), 201

    @app.route("/client_parkings", methods=["POST"])
    def parking_entrance():
        """
        Заезд на парковку, создание client_parking

        body:

        {
        "client_id": 2,
        "parking_id": 1
        }
        """

        client_parking_schema = ClientParkingSchema()
        data = request.json

        parking_id = data["parking_id"]
        client_id = data["client_id"]

        # проверяем что такой клиент и такая парковка существует
        try:
            parking = Parking.check_parking_by_id(parking_id)
            client = Client.check_client_by_id(client_id)

        except NoResultFound as exc:
            return jsonify(error=exc.args), 404

        # проверяем что на парковке открыта
        # (закрывается когда места на парковке кончаются)
        if parking.opened is False:
            return jsonify(error="There are no seats"), 400

        client_parking = (
            db.session.query(ClientParking)
            .filter(
                ClientParking.parking_id == parking_id,
                ClientParking.client_id == client_id,
            )
            .first()
        )

        # проверяем что клиента нет на этой парковке и
        # обновляем время заезда и обнуляем время выезда
        if client_parking is not None:
            if client_parking.time_out is None:
                return jsonify(
                    error="The client is already in the parking lot"
                ), 400
            time_in = datetime.now()
            client_parking.time_in = time_in
            client_parking.time_out = None
            parking.count_available_places -= 1
            db.session.commit()
            return client_parking_schema.dump(client_parking), 201

        # фиксируем время заезда
        time_in = datetime.now()

        # добавляем нового клиента на парковку
        client_parking = ClientParking(
            client_id=client.id, parking_id=parking.id, time_in=time_in
        )

        db.session.add(client_parking)
        parking.count_available_places -= 1

        if parking.count_available_places < 1:
            parking.opened = 0

        db.session.commit()

        return client_parking_schema.dump(client_parking), 201

    @app.route("/client_parkings", methods=["DELETE"])
    def exit_from_parking():
        """
        Выезд с парковки, удаление client_parking

        body:

        {
        "client_id": 2,
        "parking_id": 2
        }
        """
        client_parking_schema = ClientParkingSchema()
        data = request.json

        parking_id = data["parking_id"]
        client_id = data["client_id"]

        # пробуем получить client_parking по id клиента и парковки
        try:
            client_parking = (
                db.session.query(ClientParking)
                .filter(
                    ClientParking.client_id == client_id,
                    ClientParking.parking_id == parking_id,
                )
                .one()
            )

        except NoResultFound:
            return (
                jsonify(
                    NoResultFound="Such client parking connection not found"
                ), 404
            )

        # Если время выезда установлено значит клиент уже не на парковке
        if client_parking.time_out is not None:
            return jsonify(
                error="The client has already left the parking lot"
            ), 400

        # Проверяем что у клиента привязана карта
        if client_parking.client.credit_card is None:
            db.session.rollback()
            return jsonify(
                NotCreditCard="The client does not have a credit card"
            ), 404

        client_parking.parking.count_available_places += 1
        date_out = datetime.now()
        client_parking.time_out = date_out

        db.session.commit()

        return client_parking_schema.dump(client_parking), 201

    @app.route("/clients/add-card", methods=["POST"])
    def add_card_client():
        """
        Добавить карту клиенту или изменить

        body:

        {
        "client_id": 1,
        "credit_card": "123"
        }
        """

        client_schema = ClientSchema()
        data = request.json

        client_id = data["client_id"]
        credit_card = data["credit_card"]

        try:
            client = Client.check_client_by_id(client_id)

        except NoResultFound as exc:
            return jsonify(error=exc.args), 404

        client.credit_card = credit_card
        db.session.commit()

        return client_schema.dump(client)

    return app
