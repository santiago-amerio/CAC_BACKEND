#
#   !!! antes que nada corre pip install -r req.txtt !!!
#
from flask import Flask, jsonify, request, render_template, make_response


# del modulo flask importar la clase Flask y los métodos jsonify,request
from flask_cors import CORS  # del modulo flask_cors importar CORS
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow


import modules.auth as auth
from modules.auth import needs_auth_decorator
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


class Routes:
    def __init__(self, app):
        self.app = app

        self.route_list = [
            {
                "endpoint": "login",
                "method": ["POST"],
                "function": [
                    self.send_token,
                ],
            },
            {
                "endpoint": "user",
                "method": ["GET", "POST", "PATCH", "DELETE"],
                "function": [
                    self.__get_user,
                    self.__post_user,
                    self.__patch_user,
                    self.__delete_user,
                ],
            },
            {
                "endpoint": "category",
                "method": ["GET", "POST", "PATCH", "DELETE"],
                "function": [
                    self.__get_category,
                    self.__post_category,
                    self.__patch_category,
                    self.__delete_category,
                ],
            },
            {
                "endpoint": "product",
                "method": ["GET", "POST", "PATCH", "DELETE"],
                "function": [
                    self.__get_product,
                    self.__post_product,
                    self.__patch_product,
                    self.__delete_product,
                ],
            },
        ]

        self.register_routes()

        def __post_init__(self):
            self.initialize_root("root", "changeme")

    def register_routes(self):
        # self.app.add_url_rule("/singup", view_func=self.create_user, methods=["PUT"])

        for rule in self.route_list:
            list_method_funciton = list(
                map(list, list(zip(rule["method"], rule["function"])))
            )
            for method, function in list_method_funciton:
                self.app.add_url_rule(
                    f"/{rule['endpoint']}", view_func=function, methods=[method]
                )
        self.app.add_url_rule(
            "/clear_tokens", view_func=self.clear_tokens, methods=["GET"]
        )
        self.app.add_url_rule("/", view_func=self.home_POST, methods=["POST"])
        self.app.add_url_rule("/", view_func=self.home_GET, methods=["GET"])

    def send_token(self):
        name = request.json["name"]
        user = User.query.filter_by(name=name).first()
        response, token = auth.login(user, request.json)
        if response.status_code == 200:
            new_token = Token(user.id, token)
            db.session.add(new_token)
            db.session.commit()
            return response
        else:
            return response.json

    def clear_tokens(self):
        return auth.clear_timed_out_tokens(db, Token)

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

    @needs_auth_decorator(db, User, Token, request)
    def create_product(self):
        nombre = request.json["nombre"]
        precio = request.json["precio"]
        stock = request.json["stock"]
        imagen = request.json["imagen"]
        new_producto = Producto(nombre, precio, stock, imagen)
        db.session.add(new_producto)
        db.session.commit()
        return producto_schema.jsonify(new_producto)

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

    def product_management(self):
        return

    @needs_auth_decorator(db, User, Token, request)
    def __get_user(self):
        user = request.args.get("name")
        # si le damos un user devuelve la id y nombre de ese user
        # si no le especificamos user, devuelve la lista completa de id y nombre
        if user:
            query = User.query.filter_by(name=user)
            query = query.with_entities(User.name, User.id).first()
            response = query
            serialized_data = user_schema.dump(response)
            return serialized_data
        else:
            response = User.query.with_entities(User.name, User.id).all()
            return users_schema.dump(response)

    # genera nuevo usuario
    # devuelve id y nombre
    @needs_auth_decorator(db, User, Token, request, admin=True)
    def __post_user(self):
        name = request.json["name"]
        passw = auth.generate_password()
        new_user = User(name, passw)
        db.session.add(new_user)
        try:
            db.session.commit()
        except:
            return "Usuario ya registrado?"
        response = User.query.filter_by(name=name).first()

        return user_schema.jsonify(response)

    # actualiza contraseña (solo del propio usuario)
    @needs_auth_decorator(db, User, Token, request)
    def __patch_user(self):
        user_name = request.cookies["token"].split(".")[0]
        user = User.query.filter_by(name=user_name).first()

        if "passw" in request.json:
            user.passw = request.json["passw"]
            db.session.commit()
            cleared = auth.clear_user_token(db, User, Token, user_name)
            return "cambio contraseña " + cleared

        return 'err, necesitas proporcionar un campo "passw" para modificar la contraseña'  # update

    # cambia la flag active en la base de datos a false
    @needs_auth_decorator(db, User, Token, request, admin=True)
    def __delete_user(self):
        if not "name" in request.json:
            return "proporciona el nombre de la cuenta a desactivar {'nombre':'account-name'}"
        user_name = request.json["name"]
        user = User.query.filter_by(name=user_name).first()
        user.active = False
        db.session.commit()
        return producto_schema.jsonify(user)

    ##################### category functions

    def __get_category(self):
        title = request.args.get("titulo")
        print(title)
        if title:
            query = Category.query.filter_by(titulo=title).first()

            serialized_data = category_schema.dump(query)
            return serialized_data
        else:
            response = Category.query.all()
            response = categories_schema.dump(response)
            return jsonify(response)

    # all_productos = Producto.query.all()
    # result = productos_schema.dump(all_productos)
    # return jsonify(result)
    @needs_auth_decorator(db, User, Token, request)
    def __post_category(self):
        title = request.json["titulo"]
        description = request.json["descripcion"]
        img_url = request.json["imagen"]

        new_category = Category(title, img_url, description)
        db.session.add(new_category)
        try:
            db.session.commit()
        except:
            return "categoria ya existe?"
        response = Category.query.filter_by(titulo=title).first()

        return category_schema.jsonify(response)

    @needs_auth_decorator(db, User, Token, request)
    def __patch_category(self):
        json = request.json
        if not "id" in json:
            return "necesitas la id de la categoria para actualizarla"
        cat = Category.query.filter_by(id=json["id"])
        if "titulo" in json:
            cat.titulo = json["titulo"]

        if "descripcion" in json:
            cat.description = json["descripcion"]

        if "imagen" in json:
            cat.imagen = json["imagen"]

        db.session.commit()
        data = Category.query.get(json["id"])
        dump = category_schema.dump(data)
        return dump

    @needs_auth_decorator(db, User, Token, request)
    def __delete_category(self):
        if not "id" in request.json:
            return "proporciona la id de la categoria a desactivar"
        category_id = request.json["id"]
        category = Category.query.filter_by(id=category_id).first()
        category.active = False
        db.session.commit()
        return category_schema.jsonify(category)

    def __get_product(self):
        json = request.json
        query = False
        if "modelo" in json:
            query = Producto.query.filter_by(modelo=json["modelo"]).first()
        elif "id" in json:
            query = Producto.query.filter_by(id=json["id"]).first()
        if query:
            serialized_data = producto_schema.dump(query)
            return serialized_data
        elif "categoria" in json:
            response = Producto.query.filter_by(categoria=json["categoria"]).all()
            response = productos_schema.dump(response)
            return jsonify(response)
        else:
            response = Producto.query.all()
            response = productos_schema.dump(response)
            return jsonify(response)

    def __post_product(self):
        json = request.json
        model = json["modelo"]
        price = json["precio"]
        img = json["imagen"]
        description = json["descripcion"]
        category = json["categoria"]
        category_exist = Category.query.filter_by(id=category).first()

        is_in_db = Producto.query.filter_by(modelo=model).first()
        if not category_exist:
            return "la categoria no existe, por favor crea la categoria primero."
        if is_in_db:
            return "producto ya existe."
        new_product = Producto(model, price, img, description, category)
        db.session.add(new_product)
        try:
            db.session.commit()
        except Exception as e:
            print(e)
            return "Ocurrio un error al insertar en la base de datos"
        response = Producto.query.filter_by(modelo=model).first()

        return producto_schema.jsonify(response)

    def __patch_product(self):
        return "test"

    def __delete_product(self):
        return "test"


# Create the routes
routes_instance = Routes(app)


if __name__ == "__main__":
    app.run(debug=True, port=5000)  # ejecuta el servidor Flask en el puerto 5000
