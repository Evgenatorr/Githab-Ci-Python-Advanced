from parking_app.my_app import create_app
from parking_app.config import AppConfig

if __name__ == "__main__":
    app = create_app(config=AppConfig)
    app.run(debug=True)
