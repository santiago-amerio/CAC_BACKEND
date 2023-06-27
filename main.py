#
#   !!! antes que nada corre pip install -r req.txtt !!!
#
from flask import Flask, jsonify, request, render_template

# del modulo flask importar la clase Flask y los métodos jsonify,request
from flask_cors import CORS  # del modulo flask_cors importar CORS
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow


from modules.login import authentication
from modules.auth import check_user_token
from modules.instructions import instructions_post

app = Flask(__name__)  # crear el objeto app de la clase Flask
CORS(app)  # modulo cors es para que me permita acceder desde el frontend al backend
import os

from dotenv import load_dotenv

load_dotenv()

# env variables for db connection
DB_protocol = os.getenv("MYSQL_PROTOCOL")
DB_user = os.getenv("MYSQL_USER")
DB_passw = os.getenv("MYSQL_PASSW")
DB_host = os.getenv("MYSQL_HOST")
DB_db_name = os.getenv("MYSQL_DB_NAME")

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
    name = db.Column(db.String(100))
    passw = db.Column(db.String(100))

    def __init__(self, name, passw):
        print(name, passw)  # crea el  constructor de la clase
        self.name = name
        self.passw = passw


class Token(db.Model):  # la clase Producto hereda de db.Model
    id = db.Column(db.Integer, primary_key=True)  # define los campos de la tabla
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    token = db.Column(db.String(150))

    def __init__(self, user_id, token):
        self.user_id = user_id
        self.token = token


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


@app.route("/singup", methods=["PUT"])
def create_user():
    name = request.json["name"]
    passw = request.json["passw"]
    new_user = User(name, passw)
    db.session.add(new_user)
    db.session.commit()

    return user_schema.jsonify(new_user)


@app.route("/login", methods=["POST"])
def send_token():
    name = request.json["name"]
    user = User.query.filter_by(name=name).first()
    token = authentication(user, request.json)
    if token:
        new_token = Token(user.id, token)
        db.session.add(new_token)
        db.session.commit()
        return jsonify(token)
    else:
        return "error"


# crea los endpoint o rutas (json)
@app.route("/productos", methods=["GET"])
def get_Productos():
    all_productos = Producto.query.all()  # el metodo query.all() lo hereda de db.Model
    result = productos_schema.dump(
        all_productos
    )  # el metodo dump() lo hereda de ma.schema y
    # trae todos los registros de la tabla
    return jsonify(result)  # retorna un JSON de todos los registros de la tabla


@app.route("/productos/<id>", methods=["GET"])
def get_producto(id):
    producto = Producto.query.get(id)
    return producto_schema.jsonify(
        producto
    )  # retorna el JSON de un producto recibido como parametro


@app.route("/productos/<id>", methods=["DELETE"])
def delete_producto(id):
    producto = Producto.query.get(id)
    db.session.delete(producto)
    db.session.commit()
    return producto_schema.jsonify(
        producto
    )  # me devuelve un json con el registro eliminado


@app.route("/productos", methods=["POST"])  # crea ruta o endpoint
def create_producto():
    is_authenticated = check_user_token(db, User, Token, request.json)
    if is_authenticated:
        # print(request.json)  # request.json contiene el json que envio el cliente
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


@app.route("/productos/<id>", methods=["PUT"])
def update_producto(id):
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


@app.route("/", methods=["POST"])
def home_POST():
    return instructions_post()


@app.route("/", methods=["GET"])
def home_GET():
    return render_template(
        "instructions_template.html", instructions=instructions_post()
    )

    # programa principal *******************************


if __name__ == "__main__":
    app.run(debug=True, port=5000)  # ejecuta el servidor Flask en el puerto 5000
