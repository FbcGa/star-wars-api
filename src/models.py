from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

#relacion de uno a muchos entre usuarios y favoritos
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    favorites = db.relationship('Favorite', backref='user')

    def __repr__(self):
        return '<User %r>' % self.email

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
        }

class Character(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    birth_year = db.Column(db.Integer, nullable=False)
    eye_color = db.Column(db.String(120), nullable=False)
    hair_color = db.Column(db.String(120), nullable=False)

    planets = db.relationship('CharacterPlanet', backref='characters', lazy=True)

    def __repr__(self):
        return '<Character %r>' % self.name

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "birth_year": self.birth_year,
            "eye_color": self.eye_color,
            "hair_color": self.hair_color,
        }

class Planet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    rotation_period = db.Column(db.Integer, nullable=False)
    diameter = db.Column(db.String(120), nullable=False)
    climate = db.Column(db.String(120), nullable=False)

    characters = db.relationship('CharacterPlanet', backref='planet', lazy=True)

    def __repr__(self):
        return '<Planet %r>' % self.name

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "rotation_period": self.rotation_period,
            "diameter": self.diameter,
            "climate": self.climate,
        }

class CharacterPlanet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    planet_id = db.Column(db.Integer, db.ForeignKey('planet.id'))
    character_id = db.Column(db.Integer, db.ForeignKey('character.id'))
    
    def serialize(self):
        return {
            "id": self.id,
            "episodes": self.episode_id,
            "characters": self.character_id,
            }

    def __repr__(self):
        return f'<CharacterApperances character: {self.character_id} episode: {self.episode_id}>'
    
class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    character_id = db.Column(db.Integer, db.ForeignKey('character.id'))
    planet_id = db.Column(db.Integer, db.ForeignKey('planet.id'))

    character = db.relationship("Character", backref="favorites")
    planet = db.relationship("Planet", backref="favorites")

    def __repr__(self):
        return '<Favorite %r>' % self.user_id

    def serialize(self):
        return {
            "id": self.id,
            "user": self.user,
            "character": self.character,
            "planet": self.planet
        }