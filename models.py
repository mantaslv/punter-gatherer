from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Game(db.Model):
    __tablename__ = 'game_data'
    id = db.Column(db.Integer, primary_key=True)
    competition = db.Column(db.String(50))
    home_team = db.Column(db.String(50))
    away_team = db.Column(db.String(50))

    def __repr__(self):
        return f"<Game id={self.id}, comp={self.competition}, home_team={self.home_team}, away_team={self.away_team}>"