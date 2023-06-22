from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost:5432/punter_gatherer'

db = SQLAlchemy(app)

class Game(db.Model):
    __tablename__ = 'game_data'
    id = db.Column(db.Integer, primary_key=True)
    comp = db.Column(db.String(50))
    hometeam = db.Column(db.String(50))
    awayteam = db.Column(db.String(50))

    def __repr__(self):
        return f"<Game id={self.id}, comp={self.comp}>"

@app.route('/games')
def get_games():
    games = Game.query.all()
    game_list = []

    for game in games:
        game_list.append({
            'id': game.id,
            'comp': game.comp,
            'hometeam': game.hometeam,
            'awayteam': game.awayteam,
        })

    return jsonify(game_list)
