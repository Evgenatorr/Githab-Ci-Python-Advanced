from datetime import datetime

from flask_sqlalchemy.model import DefaultMeta
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    VARCHAR,
    BOOLEAN,
    DATETIME,
    UniqueConstraint,
)
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import relationship

db = SQLAlchemy()

Model: DefaultMeta = db.Model

class Client(Model):
    """
    Модель списка клиентов
    """

    __tablename__: str = "clients"

    id: Column[int] = Column(Integer, primary_key=True)
    name: Column[str] = Column(VARCHAR(50), nullable=False)
    surname: Column[str] = Column(VARCHAR(50), nullable=False)
    credit_card: Column[str] = Column(VARCHAR(50), default=None)
    car_number: Column[str] = Column(VARCHAR(10))

    @classmethod
    def check_client_by_id(cls, client_id):
        client = (db.session.query(cls)
                  .filter(cls.id == client_id)
                  .one_or_none())
        if client:
            return client
        raise NoResultFound("There is no client with this id")
# type: ignore[name-defined]


class Parking(Model):
    """
    Модель описание парковок
    """

    __tablename__: str = "parkings"

    id: Column[int] = Column(Integer, primary_key=True)
    address: Column[str] = Column(VARCHAR(100), unique=True, nullable=False)
    opened: Column[bool] = Column(BOOLEAN, default=True)
    count_places: Column[int] = Column(Integer, nullable=False)
    count_available_places: Column[int] = Column(Integer)

    @classmethod
    def check_parking_by_id(cls, parking_id):
        parking = (db.session.query(cls)
                   .filter(cls.id == parking_id)
                   .one_or_none())
        if parking:
            return parking
        raise NoResultFound("There is no parking with this id")
# type: ignore[name-defined]


class ClientParking(Model):
    """
    Модель описание клиент-парковка
    """

    __tablename__: str = "client_parking"

    id: Column[int] = Column(Integer, primary_key=True)
    client_id: Column[int] = Column(Integer, ForeignKey("clients.id"))
    parking_id: Column[int] = Column(Integer, ForeignKey("parkings.id"))
    time_in: Column[datetime] = Column(DATETIME, default=None)
    time_out: Column[datetime] = Column(DATETIME, default=None)
    UniqueConstraint(client_id, parking_id, name="unique_client_parking")

    parking = relationship("Parking", backref="parkings")
    client = relationship("Client", backref="clients")
# type: ignore[name-defined]
