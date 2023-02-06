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

#[GET] /people - Listar todos los registros de people en la base de datos
@app.route('/people', methods=['GET'])
def handle_characters():
    all_people = People.query.all()
    # query.all() es un método de SQLAlchemy que se utiliza para recuperar todos los registros de una tabla en la base de datos. La llamada a query.all() devuelve una lista de objetos que representan todas las filas en la tabla correspondiente en la base de datos.
    
    #En el anterior ejemplo, se llama a Characters.query.all() para recuperar todos los personajes de la base de datos y almacenarlos en la variable all_characters.
    #/////////////////////////////////////////////////////////////////////////////////////////
    results = list(map(lambda item: item.serialize(),all_people))
    #list(map(lambda item: item.serialize(), all_characters)) es una operación de programación funcional que aplica una función serialize a cada elemento de la lista all_characters. La función serialize se supone que devuelve una representación serializada de un objeto, como un diccionario.

    #La función map recorre la lista all_characters y aplica la función serialize a cada uno de sus elementos. El resultado es un objeto mapa que contiene la salida de serialize para cada elemento de la lista all_characters. Finalmente, se convierte el objeto mapa en una lista con la función list. La variable results contiene la lista resultante.
    return jsonify(results), 200
#-------------------------------------------------------------------------------------------------
#[GET] /people/<int:people_id> Listar la información de una sola people
@app.route('/people/<int:people_id>', methods=['GET'])
#Este código es una función de Flask que define un endpoint de tipo GET en la URL "/people/int:character_id". La función recupera un personaje específico de una base de datos basada en SQLAlchemy, utilizando un identificador de personaje (character_id) que se pasa como parámetro en la URL.
def get_info_people(people_id):
    people = People.query.filter_by(id=people_id).first()
    #La función utiliza Characters.query.filter_by(id=character_id).first() para recuperar el personaje con el identificador especificado en la base de datos. Si el personaje no existe, se devuelve un mensaje de error con un código de estado 404 Not Found. De lo contrario, se serializa el personaje con la función serialize y se devuelve como una respuesta JSON con un código de estado 200 OK.
    return jsonify(people.serialize()), 200
#-------------------------------------------------------------------------------------------------
#[GET] /planets Listar los registros de planets en la base de datos
@app.route('/planets', methods=['GET'])
#Este código es una función de Flask que define un endpoint de tipo GET en la URL "/planets". La función recupera todos los planetas de una base de datos basada en SQLAlchemy con Planets.query.all() y los serializa utilizando una expresión lambda y la función serialize. Luego, la lista serializada se devuelve como una respuesta JSON con un código de estado 200 OK.
def handle_planet():
    all_planets = Planets.query.all()
    results = list(map(lambda item: item.serialize(),all_planets))
    return jsonify(results), 200
#-------------------------------------------------------------------------------------------------
#[GET] /planets/<int:planet_id> Listar la información de un solo planet
@app.route('/planets/<int:planet_id>', methods=['GET'])
#Este código es una función de Flask que define un endpoint de tipo GET en la URL "/planets/int:planet_id". La función recupera un solo planeta de una base de datos basada en SQLAlchemy filtrando por su identificador con Planets.query.filter_by(id=planet_id).first(). Si el planeta no existe, se devuelve un mensaje de error como respuesta JSON con un código de estado 404 NOT FOUND. Si el planeta existe, se serializa con la función serialize y se devuelve como respuesta JSON con un código de estado 200 OK.
def handle_one_planet(planet_id):
    one_planet = Planets.query.filter_by(id=planet_id).first()
    if one_planet is None:
        return jsonify({"msg":"planeta no existente"}), 404
    else:
        return jsonify(one_planet.serialize()), 200
#-----------------------------------------------------------------------------------------
#GET user - Listar todos los usuarios del blog
@app.route('/user', methods=['GET'])
def handle_allusers():
    allUsers = User.query.all()
    results = list(map(lambda item: item.serialize(),allUsers))
    return jsonify(results), 200

# GET users favorites - Listar todos los favoritos que pertenecen al usuario actual
@app.route('/user/<int:user_id>/likes', methods=['GET'])
def get_user_favorites(user_id):
    favorites = Likes.query.filter_by(user_id=user_id).all()
    results = list(map(lambda item: item.serialize(), favorites))
    return jsonify(results), 200
#-----------------------------------------------------------------------------------------
#[POST] /favorite/planet/<int:planet_id> Añade un nuevo planet favorito al usuario actual con el planet id = planet_id.
@app.route('/likes/planets/<int:user_ID>/<int:planet_ID>', methods=['POST'])
#El código se trata de una función de ruta en Flask que se ejecuta al hacer una solicitud HTTP POST a la dirección "/favourites/planets/int:user_ID/int:planet_ID". La función realiza las siguientes acciones:
def add_NewFavPlanets(user_ID, planet_ID):
	planet = Likes.query.filter_by(planets_id=planet_ID,user_id=user_ID).first()
    #1. Verifica si un planeta ya está marcado como favorito por el usuario especificado (a través de planet = Favourites.query.filter_by(planet_id=planet_ID,user_id=user_ID).first()).
	if planet is None:
		existe = Planets.query.filter_by(id=planet_ID).first()
        #2. Si el planeta no está marcado como favorito, verifica si existe (a través de existe = Planets.query.filter_by(id=planet_ID).first()).
		if existe is None:
			response_body = {"msg":"El planeta no existe"}
			return jsonify(response_body), 404
		else:
			user = User.query.filter_by(id=user_ID).first()
            #3. Si el planeta existe, verifica si el usuario especificado existe (a través de user = User.query.filter_by(id=user_ID).first()).
			if user is None:
				response_body = {"msg":"El usuario no existe"}
				return jsonify(response_body), 404
			else:
                #4. Si el usuario existe, agrega el planeta como favorito en la base de datos (a través de favorito = Favourites(planet_id=planet_ID,user_id=user_ID), db.session.add(favorito) y db.session.commit()).
				favorito = Likes(planets_id=planet_ID,user_id=user_ID)
				db.session.add(favorito)
				db.session.commit()
				response_body = {"msg":"Se ha agregado el planeta a favoritos"}
                #5. Devuelve una respuesta JSON con un mensaje que indica si se agregó el planeta como favorito o si ya existía.
				return jsonify(response_body), 200
	else:
		response_body = {"msg":"El planeta ya está agregado"}
		return jsonify(response_body), 404
#-------------------------------------------------------------------------------------------------
#[POST] /favorite/people/<int:planet_id> Añade una nueva people (personaje) favorita al usuario actual con el people.id = people_id.
@app.route('/likes/people/<int:user_ID>/<int:character_ID>', methods=['POST'])
#Este código define una ruta web para agregar un personaje a la lista de favoritos de un usuario en una aplicación. La ruta acepta dos parámetros en la URL, user_ID y character_ID, que identifican al usuario y al personaje que se desea agregar a favoritos, respectivamente.
def add_NewFavCharacter(user_ID, character_ID):
    #La función add_NewFavCharacter verifica si el personaje y el usuario existen en las bases de datos correspondientes (Characters y User). Si ambos existen, la función crea una nueva entrada en la tabla Likes que relaciona al usuario con el personaje y agrega esta entrada a la base de datos. Finalmente, la función devuelve una respuesta en formato JSON que indica que el personaje se ha agregado a favoritos con éxito o, en caso contrario, que ya está agregado o que no existe.

	# Aquí verificamos si el usuario ingresado existe
	character = Likes.query.filter_by(people_id=character_ID,user_id=user_ID).first()
	if character is None:
		existe = People.query.filter_by(id=character_ID).first()
		if existe is None:
			response_body = {"msg":"El personaje no existe"}
			return jsonify(response_body), 404
		else:
			user = User.query.filter_by(id=user_ID).first()
			if user is None:
				response_body = {"msg":"El usuario no existe"}
				return jsonify(response_body), 404
			else:
				favorito = Likes(people_id=character_ID,user_id=user_ID)
				db.session.add(favorito)
				db.session.commit()
				response_body = {"msg":"Se ha agregado el personaje a favoritos"}
				return jsonify(response_body), 200
	else:
		response_body = {"msg":"El personaje ya está agregado"}
		return jsonify(response_body), 404
#-----------------------------------------------------------------------------------------
#[DELETE] /favorite/planet/<int:planet_id> Elimina un planet favorito con el id = planet_id`.
@app.route('/likes/planets/<int:user_ID>/<int:planets_id>', methods=['DELETE'])
def borrar_Planet_Fav(user_ID, planets_id):
    #Esta función borra un planeta favorito específico para un usuario dado su ID en una aplicación web usando Flask. La función toma dos argumentos (user_ID y planets_id) que representan los IDs del usuario y el planeta, respectivamente. Primero, verifica si el usuario y el planeta existen en la base de datos. Si existen, busca el registro de planeta favorito en la tabla de "Likes" y lo borra. Finalmente, devuelve una respuesta en formato JSON con un mensaje indicando el resultado de la operación.
    
	# Aquí verificamos si el usuario ingresado existe
	user= User.query.filter_by(id=user_ID).first() 
	if user is None:
		response_body = {"msg": "El usuario ingresado no existe"}
		return jsonify(response_body), 404
	#Aquí verificamos si el planeta ya esté ingresado en favoritos
	planeta = Planets.query.filter_by(id=planets_id).first() 
	if planeta is None:
		response_body = {"msg": "El planeta ingresado no existe dentro de favoritos"}
		return jsonify(response_body), 404
	#Aquí le indicamos que debe borrar al planeta seleccionado
	borrar_planeta = Likes.query.filter_by(user_id=user_ID).filter_by(planets_id=planets_id).first()
	if borrar_planeta is None:
		response_body = {"msg": "El planeta ingresado no existe dentro de favoritos"}
		return jsonify(response_body), 404
	else:
		db.session.delete(borrar_planeta)
		db.session.commit()
		response_body = {"msg": "El planeta seleccionado fue borrado con exito"}
		return jsonify(response_body), 200
#-----------------------------------------------------------------------------------------
#[DELETE] /favorite/people/<int:people_id> Elimina una people favorita con el id = people_id.
@app.route('/likes/people/<int:user_ID>/<int:people_ID>', methods=['DELETE'])
def borrar_People_Fav(user_ID, people_ID):
	# Aquí verificamos si el usuario ingresado existe
	user= User.query.filter_by(id=user_ID).first() 
	if user is None:
		response_body = {"msg": "El usuario ingresado no existe"}
		return jsonify(response_body), 404
	#Aquí verificamos si el planeta ya esté ingresado en favoritos
	planeta = People.query.filter_by(id=people_ID).first() 
	if planeta is None:
		response_body = {"msg": "El personaje ingresado no existe dentro de favoritos"}
		return jsonify(response_body), 404
	#Aquí le indicamos que debe borrar al planeta seleccionado
	borrar_people = Likes.query.filter_by(user_id=user_ID).filter_by(people_id=people_ID).first()
	if borrar_people is None:
		response_body = {"msg": "El personaje ingresado no existe dentro de favoritos"}
		return jsonify(response_body), 404
	else:
		db.session.delete(borrar_people)
		db.session.commit()
		response_body = {"msg": "El personaje seleccionado fue borrado con exito"}
		return jsonify(response_body), 200

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)