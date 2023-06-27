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


@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200


@app.route('/character/<int:id>', methods=['GET'])
def get_character_by_id(id):
    character = Character.query.filter_by(id=id).first()

    if not character:
        return {"error": "There is no character with that id"}, 404

    return jsonify({"character": character.serialize()})


@app.route('/planet/<int:id>', methods=['GET'])
def get_planet_by_id(id):
    planet = Planet.query.filter_by(id=id).first()

    if not planet:
        return {"error": "There is no character with that id"}, 404

    return jsonify({"planet": planet.serialize()})


@app.route('/characters', methods=['GET'])
def get_characters():
    character_list = Character.query.all()
    serialized_characters = [character.serialize()for character in character_list]
    return jsonify({"characters": serialized_characters})


@app.route('/planets', methods=['GET'])
def get_planets():
    planet_list = Planet.query.all()
    serialized_planets = [planet.serialize() for planet in planet_list]
    return jsonify({"planet": serialized_planets})


@app.route('/planet', methods=['POST'])
def add_planet():
    body = request.json
    body_name = body.get('name', None)
    body_population = body.get('population', None)
    body_climate = body.get('climate', None)
    body_terrain = body.get('terrain', None)

    if body_name is None:
        return {"error": "The name field is required"}, 400

    planet_exists = Planet.query.filter_by(name=body_name).first()
    if planet_exists:
        return {"error": f"There is already a character with that name: {body_name}"}, 400

    new_planet = Planet(name=body_name, population=body_population,
                        climate=body_climate, terrain=body_terrain)
    db.session.add(new_planet)

    try:
        db.session.commit()  # commit ->
        return jsonify({"msg": "Planet Created!"}), 201

    except Exception as error:
        db.session.rollback()
        return {"error": error}, 500


@app.route('/character', methods=['POST'])
def add_character():
    body = request.json
    body_name = body.get('name', None)
    body_gender = body.get('gender', None)
    body_homeworld = body.get('homeworld', None)
    body_hair_color = body.get('hair_color', None)

    if body_name is None:
        return {"error": "The name field is required"}, 400

    character_exists = Character.query.filter_by(name=body_name).first()
    if character_exists:
        return {"error": f"There is already a Planet with that name: {body_name}"}, 400

    new_character = Character(name=body_name, gender=body_gender,homeworld=body_homeworld, hair_color=body_hair_color)
    db.session.add(new_character)

    try:
        db.session.commit()  # commit ->
        return jsonify({"msg": "Character created!"}), 201

    except Exception as error:
        db.session.rollback()
        return {"error": error}, 500


@app.route('/favorites/<int:user_id>', methods=['GET'])
def getFavoritesByUser(user_id):
    favorites = Favorite.query.filter_by(user_id=user_id)
    serialized_favorites = [favorite.serialize() for favorite in favorites]
    return jsonify({"favorites": serialized_favorites})


@app.route('/favorites/<int:user_id>/<int:planet_id>', methods=['POST'])
def addPlanetToFavorites(user_id, planet_id):
    planet = Planet.query.filter_by(id=planet_id).first()
    if planet is None:
        return jsonify({"mensaje": "Planet does not exist"}), 400
    planetFavorites = Favorite.query.filter_by(
        user_id=user_id, planet_id=planet_id).first()
    if planetFavorites is not None:
        return jsonify({"mensaje": "Planet already in favorites"}), 400
    else:
        try:
            favorite = Favorite(
                user_id=user_id, name=planet.name, planet_id=planet_id)
            db.session.add(favorite)
            db.session.commit()
            return jsonify({"mensaje": "Planet added to favorites!"}), 200
        except Exception as error:
            db.session.rollback()
            return {"error": error}, 500


@app.route('/favorite/<int:user_id>/<int:planet_id>', methods=['DELETE'])
def deletePlanetOfFavorites(user_id, planet_id):
    favoritePlanet = Favorite.query.filter_by(
        planet_id=planet_id, user_id=user_id).first()
    if favoritePlanet is None:
        return jsonify({"mensaje": "Planet not in favorites"}), 400
    else:
        try:
            db.session.delete(favoritePlanet)
            db.session.commit()
            return jsonify({"mensaje": "Planet removed from favorites"}), 200
        except Exception as error:
            db.session.rollback()
            return {"error": error.args[0]}, 500
    return


@app.route('/favorites/<int:user_id>/<int:character_id>', methods=['POST'])
def addCharacterToFavorites(user_id, character_id):
    character = Character.query.filter_by(id=character_id).first()
    if character is None:
        return jsonify({"mensaje": "Character does not exist"}), 400
    characterFavorites = Favorite.query.filter_by(
        user_id=user_id, character_id=character_id).first()
    if characterFavorites is not None:
        return jsonify({"mensaje": "Character already in favorites"}), 400
    else:
        try:
            favorite = Favorite(
                user_id=user_id, name=character.name, character_id=character_id)
            db.session.add(favorite)
            db.session.commit()
            return jsonify({"mensaje": "Character added to favorites!"}), 200
        except Exception as error:
            db.session.rollback()
            return {"error": error}, 500


@app.route('/favorite/<int:user_id>/<int:character_id>', methods=['DELETE'])
def deleteCharacterOfFavorites(user_id, character_id):
    favoriteCharacter = Favorite.query.filter_by(
        character_id=character_id, user_id=user_id).first()
    if favoriteCharacter is None:
        return jsonify({"mensaje": "Character not in favorites"}), 400
    else:
        try:
            db.session.delete(favoriteCharacter)
            db.session.commit()
            return jsonify({"mensaje": "Character removed from favorites"}), 200
        except Exception as error:
            db.session.rollback()
            return {"error": error.args[0]}, 500
    return


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
