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
from models import db, User, People, Vehicle, Planets, Likes
#from models import people

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
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

# A partir de acá se codea, lo de arriba no se toca

#GET people (characters) - Listar todos los registros de people en la base de datos
@app.route('/people', methods=['GET'])
def get_people():
    allPeople = People.query.all()
    results = list(map(lambda item: item.serialize(), allPeople))
    return jsonify(results), 200

# Listar la información de una sola people
@app.route('/people/<int:people_id>', methods=['GET'])
def get_info_people(people_id):
    people = People.query.filter_by(id=people_id).first()
    return jsonify(people.serialize()), 200



#GET planets - Listar los registros de planets en la base de datos
@app.route('/planets', methods=['GET'])
def get_planets():
    allPlanets= Planets.query.all()
    results = list(map(lambda item: item.serialize(),allPlanets))
    return jsonify(results), 200

#Listar la información de un solo planet
@app.route('/planets/<int:planets_id>', methods=['GET'])
def get_info_planet(planets_id):
    planet = Planets.query.filter_by(id=planets_id).first()

    if planet == None:
        return jsonify({"msg":"El planeta no existe"}), 404
    else:
        return jsonify(planet.serialize()), 200



#GET user - Listar todos los usuarios del blog
@app.route('/user', methods=['GET'])
def handle_allusers():
    allUsers = User.query.all()
    results = list(map(lambda item: item.serialize(),allUsers))
    return jsonify(results), 200

#GET users favorites - Listar todos los favoritos que pertenecen al usuario actual
@app.route('/user/<int:user_id>/favorites', methods=['GET'])
def get_user_favorites(user_id):
    favorites = Likes.query.filter_by(user_id=user_id).all()
    results = list(map(lambda item: item.serialize(), favorites))
    return jsonify(results), 200

# @app.route('/user/<int:user_id>', methods=['GET'])
# def get_info_user(user_id):
#     user = User.query.filter_by(id=user_id).first()
#     return jsonify(user.serialize()), 200



#GET vehicles
# @app.route('/vehicles', methods=['GET'])
# def get_vehicles():
#     allVehicles = Vehicles.query.all()
#     results = list(map(lambda item: item.serialize(),allVehicles))
#     return jsonify(results), 200

#Listar la información de un solo vehiculo
# @app.route('/vehicles/<int:vehicle_id>', methods=['GET'])
# def get_info_vehicle(vehicle_id):
#     vehicle = Vehicles.query.filter_by(id=vehicle_id).first()
#     return jsonify(vehicle.serialize()), 200



# [POST] /favorite/planet/<int:planet_id> Añade un nuevo planet favorito al usuario actual con el planet id = planet_id.

@app.route('/user/<int:user_id>/favorites/planets', methods=['POST'])
def addFavPlanet(user_id):
   
    request_body = request.json #Traemos la informacion del favorito al body
    print(request_body) #Vemos lo que trae

    #Creo el nuevo objeto, con la clase Likes
    newPlanet = Likes(user_id=user_id, people_id=None, vehicle_id=None, planets_id=request_body['planets_id']) 
    
    favs = Likes.query.filter_by(user_id=user_id, planets_id=request_body["planets_id"]).first() #Obj filtrado
    print(favs)

    if favs is None:
        newPlanet = Likes(user_id = user_id, people_id = None, vehicle_id = None, planets_id = request_body['planets_id'])
        db.session.add(newPlanet)
        db.session.commit()

        return jsonify({'msg': 'haz añadido satisfactoriamenchi el favorito'}), 200

    return jsonify(request_body), 400





#[POST] /favorite/people/<int:planet_id> Añade una nueva people favorita al usuario actual con el people.id = people_id.











#[DELETE] /favorite/planet/<int:planet_id> Elimina un planet favorito con el id = planet_id`.






# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
