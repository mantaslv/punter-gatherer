from flask import Blueprint, jsonify
from models import Game

games_bp = Blueprint('games', __name__)

@games_bp.route('/games')
def get_games():
    games = Game.query.all()
    game_list = []

    for game in games:
        game_list.append({
            'id': game.id,
            'competition': game.competition,
            'home_team': game.home_team,
            'away_team': game.away_team,
        })

    return jsonify(game_list)