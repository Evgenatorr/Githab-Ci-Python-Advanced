from marshmallow import (
    Schema,
    fields,
    validates,
    ValidationError,
    post_load,
    validates_schema,
)

from .models import Client, ClientParking, Parking


class BaseSchema(Schema):
    id = fields.Int(dump_only=True)


class ClientSchema(BaseSchema):
    name = fields.Str(required=True)
    surname = fields.Str(required=True)
    credit_card = fields.Str()
    car_number = fields.Str()

    @validates("car_number")
    def check_len_car_number(self, car_number: str) -> None:
        if len(car_number) > 10:
            raise ValidationError(
                "the length car_number should not be more than 10"
            )

    @post_load
    def create_client(self, data: dict, **kwargs) -> Client:
        return Client(**data)


class ParkingSchema(BaseSchema):
    address = fields.Str(required=True)
    opened = fields.Bool()
    count_places = fields.Int(required=True, strict=True)
    count_available_places = fields.Int(required=True)

    @validates_schema
    def check_available_places(self, data, **kwargs) -> None:

        if data["count_available_places"] > data["count_places"]:
            raise ValidationError(
                "Count_available_places cannot be greater than count_places"
            )

    @validates("count_places")
    def check_len_car_number(self, count_places) -> None:
        if count_places < 1:
            raise ValidationError("count_places cannot be less than 1")

    @post_load
    def create_parking(self, data: dict, **kwargs) -> Parking:
        return Parking(**data)


class ClientParkingSchema(BaseSchema):
    client_id = fields.Int(required=True)
    parking_id = fields.Int(required=True)
    time_in = fields.DateTime()
    time_out = fields.DateTime()

    @post_load
    def create_client_parking(self, data: dict, **kwargs) -> ClientParking:
        return ClientParking(**data)
