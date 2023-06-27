from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            # do not serialize the password, its a security breach
        }

class Character (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.String(20), nullable=True, default='n/a')
    homeworld = db.Column(db.String(50), nullable=True, default='n/a')
    hair_color = db.Column(db.String(20), nullable=True, default='n/a')

    def __repr__(self):
        return '<Character %r>' % self.name

    def serialize(self):
        return {
            "id":  self.id,
            "name": self.name,
            "homeworld": self.homeworld,
            "gender": self.gender,
            "hair_color": self.hair_color,
        }

class Planet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    population = db.Column(db.Integer, nullable=True, default=0)
    climate = db.Column(db.String(80), nullable=True, default='unknown')
    terrain = db.Column(db.String(75), nullable=True, default='unknown')

    def __repr__(self):
        return '<Planet %r>' % self.name

    def serialize(self):
        return {
            "id":  self.id,
            "name": self.name,
            "population": self.population,
            "climate": self.climate,
            "terrain": self.terrain,
        } 

class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    character_id = db.Column(db.Integer, db.ForeignKey("character.id"))
    planet_id = db.Column(db.Integer, db.ForeignKey("planet.id"))
    name = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return '<Favorite %r>' % self.name

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "character_id": self.character_id,
            "planet_id": self.planet_id,
            "name": self.name,
        }