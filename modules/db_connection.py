from flask import Flask

# del modulo flask importar la clase Flask y los métodos jsonify,request
from flask_cors import CORS  # del modulo flask_cors importar CORS
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from datetime import datetime

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


class User(db.Model):  # la clase Producto hereda de db.Model
    id = db.Column(db.Integer, primary_key=True)  # define los campos de la tabla
    name = db.Column(db.String(100), unique=True)
    passw = db.Column(db.String(100))
    admin = db.Column(db.Boolean)
    active = db.Column(db.Boolean)

    def __init__(self, name, passw, admin=False, active=True):
        self.name = name
        self.passw = passw
        self.admin = admin
        self.active = active


class Token(db.Model):  # la clase Producto hereda de db.Model
    id = db.Column(db.Integer, primary_key=True)  # define los campos de la tabla
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    token = db.Column(db.String(150))
    creation_date = db.Column(db.DateTime())

    def __init__(self, user_id, token):
        self.user_id = user_id
        self.token = token
        self.creation_date = datetime.now()


class Producto(db.Model):  # la clase Producto hereda de db.Model
    id = db.Column(db.Integer, primary_key=True)  # define los campos de la tabla
    modelo = db.Column(db.String(100), unique=True)
    precio = db.Column(db.Integer)
    imagen = db.Column(db.String(400))
    description = db.Column(db.String(500))
    categoria = db.Column(db.Integer, db.ForeignKey("category.id"))
    active = db.Column(db.Boolean)

    def __init__(
        self, modelo, precio, imagen, description, categoria, active=True
    ):  # crea el  constructor de la clase
        self.modelo = modelo  # no hace falta el id porque lo crea sola mysql por ser auto_incremento
        self.precio = precio
        self.imagen = imagen
        self.description = description
        self.categoria = categoria
        self.active = active


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # define los campos de la tabla
    titulo = db.Column(db.String(100), unique=True)
    description = db.Column(db.String(1000))
    imagen = db.Column(db.String(400))
    active = db.Column(db.Boolean)

    def __init__(
        self, titulo, imagen, description, active=True
    ):  # crea el  constructor de la clase
        self.titulo = titulo  # no hace falta el id porque lo crea sola mysql por ser auto_incremento
        self.description = description
        self.imagen = imagen
        self.active = active


def initialize_root(name, passw):
    new_user = User(name, passw, admin=True)
    db.session.add(new_user)
    try:
        db.session.commit()
        print("root user created")
    except:
        print("already created")


with app.app_context():
    db.create_all()  # aqui crea todas las tablas
    initialize_root("root", "changeme")


#  ************************************************************
class ProductoSchema(ma.Schema):
    class Meta:
        fields = (
            "id",
            "modelo",
            "precio",
            "imagen",
            "description",
            "categoria",
            "active",
        )


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


class CategorySchema(ma.Schema):
    class Meta:
        fields = ("id", "titulo", "description", "imagen", "active")


category_schema = (
    CategorySchema()
)  # El objeto producto_schema es para traer un producto
categories_schema = CategorySchema(
    many=True
)  # El objeto productos_schema es para traer multiples registros de producto
