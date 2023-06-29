#
#   !!! antes que nada corre pip install -r req.txtt !!!
#
from flask import Flask, jsonify, request, render_template


# del modulo flask importar la clase Flask y los métodos jsonify,request
from flask_cors import CORS  # del modulo flask_cors importar CORS
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow


from modules.auth import check_user_token, login, clear_timed_out_tokens
from modules.instructions import instructions_post
from datetime import datetime, timedelta

import os

from dotenv import load_dotenv

load_dotenv()

# env variables for db connection
DB_protocol = os.getenv("MYSQL_PROTOCOL")
DB_user = os.getenv("MYSQL_USER")
DB_passw = os.getenv("MYSQL_PASSW")
DB_host = os.getenv("MYSQL_HOST")
DB_db_name = os.getenv("MYSQL_DB_NAME")

app = Flask(__name__)  # crear el objeto app de la clase Flask
CORS(app)  # modulo cors es para que me permita acceder desde el frontend al backend

# configuro la base de datos, con el nombre el usuario y la clave
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = f"{DB_protocol}://{DB_user}:{DB_passw}@{DB_host}/{DB_db_name}"
# URI de la BBDD                          driver de la BD  user:clave@URLBBDD/nombreBBDD
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # none
db = SQLAlchemy(app)  # crea el objeto db de la clase SQLAlquemy
ma = Marshmallow(app)  # crea el objeto ma de de la clase Marshmallow


# defino la tabla
class Producto(db.Model):  # la clase Producto hereda de db.Model
    id = db.Column(db.Integer, primary_key=True)  # define los campos de la tabla
    nombre = db.Column(db.String(100))
    precio = db.Column(db.Integer)
    stock = db.Column(db.Integer)
    imagen = db.Column(db.String(400))

    def __init__(
        self, nombre, precio, stock, imagen
    ):  # crea el  constructor de la clase
        self.nombre = nombre  # no hace falta el id porque lo crea sola mysql por ser auto_incremento
        self.precio = precio
        self.stock = stock
        self.imagen = imagen


class User(db.Model):  # la clase Producto hereda de db.Model
    id = db.Column(db.Integer, primary_key=True)  # define los campos de la tabla
    name = db.Column(db.String(100), unique=True)
    passw = db.Column(db.String(100))

    def __init__(self, name, passw):
        print(name, passw)  # crea el  constructor de la clase
        self.name = name
        self.passw = passw


class Token(db.Model):  # la clase Producto hereda de db.Model
    id = db.Column(db.Integer, primary_key=True)  # define los campos de la tabla
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    token = db.Column(db.String(150))
    creation_date = db.Column(db.DateTime())

    def __init__(self, user_id, token):
        self.user_id = user_id
        self.token = token
        self.creation_date = datetime.now()


with app.app_context():
    db.create_all()  # aqui crea todas las tablas


#  ************************************************************
class ProductoSchema(ma.Schema):
    class Meta:
        fields = ("id", "nombre", "precio", "stock", "imagen")


producto_schema = (
    ProductoSchema()
)  # El objeto producto_schema es para traer un producto
productos_schema = ProductoSchema(
    many=True
)  # El objeto productos_schema es para traer multiples registros de producto


class UserSchema(ma.Schema):
    class Meta:
        fields = ("id", "name", "passw")


user_schema = UserSchema()  # El objeto producto_schema es para traer un producto
users_schema = UserSchema(
    many=True
)  # El objeto productos_schema es para traer multiples registros de producto


class TokenSchema(ma.Schema):
    class Meta:
        fields = ("id", "user_id", "token", "expiration")


token_schema = TokenSchema()  # El objeto producto_schema es para traer un producto
tokens_schema = TokenSchema(
    many=True
)  # El objeto productos_schema es para traer multiples registros de producto


class Routes:
    def __init__(self, app):
        self.app = app
        self.register_routes()

    def register_routes(self):
        self.app.add_url_rule("/singup", view_func=self.create_user, methods=["PUT"])
        self.app.add_url_rule("/login", view_func=self.send_token, methods=["POST"])
        self.app.add_url_rule(
            "/productos", view_func=self.get_Productos, methods=["GET"]
        )
        self.app.add_url_rule(
            "/productos/<id>", view_func=self.get_producto, methods=["GET"]
        )
        self.app.add_url_rule(
            "/productos/<id>", view_func=self.delete_producto, methods=["DELETE"]
        )
        self.app.add_url_rule(
            "/productos", view_func=self.create_producto, methods=["POST"]
        )
        self.app.add_url_rule(
            "/productos/<id>", view_func=self.update_producto, methods=["PUT"]
        )
        self.app.add_url_rule(
            "/clear_tokens", view_func=self.clear_tokens, methods=["GET"]
        )
        self.app.add_url_rule("/", view_func=self.home_POST, methods=["POST"])
        self.app.add_url_rule("/", view_func=self.home_GET, methods=["GET"])

    def create_user(self):
        name = request.json["name"]
        passw = request.json["passw"]
        new_user = User(name, passw)
        db.session.add(new_user)
        db.session.commit()
        return user_schema.jsonify(new_user)

    def send_token(self):
        name = request.json["name"]
        user = User.query.filter_by(name=name).first()
        token = login(user, request.json)
        if token:
            new_token = Token(user.id, token)
            db.session.add(new_token)
            db.session.commit()
            return jsonify(token)
        else:
            return "error"

    def clear_tokens(self):
        return clear_timed_out_tokens(db, Token)

    def get_Productos(self):
        all_productos = Producto.query.all()
        result = productos_schema.dump(all_productos)
        return jsonify(result)

    def get_producto(self, id):
        producto = Producto.query.get(id)
        return producto_schema.jsonify(producto)

    def delete_producto(self, id):
        producto = Producto.query.get(id)
        db.session.delete(producto)
        db.session.commit()
        return producto_schema.jsonify(producto)

    def create_producto(self):
        is_authenticated = check_user_token(db, User, Token, request.json)
        if is_authenticated:
            nombre = request.json["nombre"]
            precio = request.json["precio"]
            stock = request.json["stock"]
            imagen = request.json["imagen"]
            new_producto = Producto(nombre, precio, stock, imagen)
            db.session.add(new_producto)
            db.session.commit()
            return producto_schema.jsonify(new_producto)
        else:
            return "auth Error"

    def update_producto(self, id):
        producto = Producto.query.get(id)
        nombre = request.json["nombre"]
        precio = request.json["precio"]
        stock = request.json["stock"]
        imagen = request.json["imagen"]
        producto.nombre = nombre
        producto.precio = precio
        producto.stock = stock
        producto.imagen = imagen
        db.session.commit()
        return producto_schema.jsonify(producto)

    def home_POST(self):
        return instructions_post()

    def home_GET(self):
        return render_template(
            "instructions_template.html", instructions=instructions_post()
        )


# Create the routes
routes_instance = Routes(app)


if __name__ == "__main__":
    app.run(debug=True, port=5000)  # ejecuta el servidor Flask en el puerto 5000
