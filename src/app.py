"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Character, Planet, Favorite
# from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        "postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object


@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints


@app.route('/')
def sitemap():
    return generate_sitemap(app)
# -------------------------------people-------------------------------


@app.route('/people', methods=['GET'])
def get_people():
    people = Character.query.all()
    people_serialize = [character.serialize() for character in people]

    return jsonify({"people": people_serialize}), 200


@app.route('/people/<int:id>', methods=['GET'])
def get_single_character(id):
    try:
        character = Character.query.get(id)
        if character is None:
            return jsonify({"people": "Character no found"}), 404
        return jsonify({"people": character.serialize()}), 200
    except Exception as error:
        return jsonify({"error": f"{error}"}), 500

# -------------------------------planet-------------------------------
@app.route('/planet', methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    planets_serialize = [planet.serialize() for planet in planets]

    return jsonify({"planets": planets_serialize}), 200


@app.route('/planet/<int:id>', methods=['GET'])
def get_single_planet(id):
    try:
        planet = Planet.query.get(id)
        if planet is None:
            return jsonify({"planet": "Planet not found"}),404
        return jsonify({"Planet": planet.serialize()})
    except Exception as error:
        return jsonify({"error" : f"{error}"}),500
        

# -------------------------------users-------------------------------
@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    users_serialize = [user.serialize() for user in users]

    return jsonify({"users": users_serialize}), 200

@app.route('/users/<int:user_id>/favorites', methods=['GET'])
def get_users_favorite(user_id):
    favorites = Favorite.query.filter_by(user_id=user_id)
    favorites_serialize = [favorite.serialize() for favorite in favorites]

    return jsonify({"favorites" : favorites_serialize}),200

@app.route('/users', methods=['POST'])
def add_user():
    body = request.json
    email = body.get("email", None)
    password = body.get("password", None)

    if email is None:
        return jsonify({"error": "el email es requerido"}), 400

    if password is None:
        return jsonify({"error": "el password es requerido"}), 400

    new_user = User(email=email, password=password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"usuario": new_user.serialize()}), 201

#------------------------add planet and people---------------

@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    body = request.json
    user_id = body.get("user_id", None)

    planet_exist = Favorite.query.filter_by(planet_id=planet_id).first()

    if user_id is None or planet_id is None:
        return jsonify({"error": "Missing values"}),400
    
    if planet_exist is not None:
        return jsonify({"error": f"Planet {planet_id} already exist"}),400

    new_planet = Favorite(user_id=user_id,planet_id=planet_id)

    try:
        db.session.add(new_planet)
        db.session.commit()
        db.session.refresh(new_planet)

        return jsonify({"message": f"Planet added successfully"}),201
    except Exception as error:
        return jsonify({"error": {error}}),500

@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_people(people_id):
    body = request.json
    user_id = body.get("user_id", None)

    character_exist = Favorite.query.filter_by(character_id=people_id).first()
    if user_id is None or people_id is None:
        return jsonify({"error": "missing values"}), 400

    if character_exist is not None:
        return jsonify({"error":f"Character {people_id} already exists"}), 400
    
    new_character = Favorite(user_id=user_id, character_id=people_id)

    try:
        db.session.add(new_character)
        db.session.commit()
        db.session.refresh(new_character)

        return jsonify({"message": f"Character added successfully"}),201
    
    except Exception as error:
        return jsonify({"error", {error}}), 500

#---------------------------------------delete---------------------------------------------
@app.route('/favorite/planet/<int:favorite_id>', methods=['DELETE'])
def delete_favorite_planet(favorite_id):
    try:
        planet = Favorite.query.get(favorite_id)
        if planet is None:
            return jsonify({"error":"Planet not found!"}), 404
        db.session.delete(planet)
        db.session.commit()

        return jsonify({"message":"planet deleted"}),200
    except Exception as error:
        return jsonify({"error": {error}})
    

@app.route('/favorite/people/<int:favorite_id>', methods=['DELETE'])
def delete_favorite_peoplet(favorite_id):
    try:
        character = Favorite.query.get(favorite_id)
        if character is None:
            return jsonify({"error":"Character not found!"}), 404
        db.session.delete(character)
        db.session.commit()

        return jsonify({"message":"character deleted"}),200
    except Exception as error:
        return jsonify({"error": {error}})
    

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
