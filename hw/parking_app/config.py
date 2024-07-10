class AppConfig:
    # SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///parking.db'


class TestConfig(AppConfig):
    TESTING = True
    # SQLALCHEMY_DATABASE_URI = 'sqlite://../test_parking.db'
