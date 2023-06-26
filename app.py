from flask import Flask
from routes import games_bp
from config import Config
from models import db

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

app.register_blueprint(games_bp)

if __name__ == '__main__':
    app.run()
