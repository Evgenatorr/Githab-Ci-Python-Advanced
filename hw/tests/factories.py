import factory
import factory.fuzzy as fuzzy

from parking_app.models import Client, Parking, db


class ClientFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Client
        sqlalchemy_session = db.session

    name = factory.Faker("first_name")
    surname = factory.Faker("last_name")
    credit_card = fuzzy.FuzzyChoice([None, "xxxxxx"])
    car_number = fuzzy.FuzzyText(length=10)


class ParkingFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Parking
        sqlalchemy_session = db.session

    address = factory.Faker("address")
    count_places = fuzzy.FuzzyInteger(low=1, high=100)
    count_available_places = factory.LazyAttribute(lambda a: a.count_places)
