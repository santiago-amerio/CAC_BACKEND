import os
from dataclasses import dataclass

from flask import Flask, jsonify, request, render_template

# del modulo flask importar la clase Flask y los métodos jsonify,request
from flask_cors import CORS  # del modulo flask_cors importar CORS
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow


DB_protocol = os.getenv("MYSQL_PROTOCOL")
DB_user = os.getenv("MYSQL_USER")
DB_passw = os.getenv("MYSQL_PASSW")
DB_host = os.getenv("MYSQL_HOST")
DB_db_name = os.getenv("MYSQL_DB_NAME")


class app1:
    def __init__(self):
        __DB_protocol = os.getenv("MYSQL_PROTOCOL")
        __DB_user = os.getenv("MYSQL_USER")
        __DB_passw = os.getenv("MYSQL_PASSW")
        __DB_host = os.getenv("MYSQL_HOST")
        __DB_db_name = os.getenv("MYSQL_DB_NAME")

        self.app = Flask(__name__)  # crear el objeto app de la clase Flask
        CORS(
            self.app
        )  # modulo cors es para que me permita acceder desde el frontend al backend
        self.app.config[
            "SQLALCHEMY_DATABASE_URI"
        ] = f"{__DB_protocol}://{__DB_user}:{__DB_passw}@{__DB_host}/{__DB_db_name}"
        self.app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # none
        self.db = SQLAlchemy(self.app)  # crea el objeto db de la clase SQLAlquemy
        self.ma = Marshmallow(self.app)  # crea el objeto ma de de la clase Marshmallow


# defino la tabla
class Producto(app1.db.Model):  # la clase Producto hereda de db.Model
    id = app1.db.Column(
        app1.db.Integer, primary_key=True
    )  # define los campos de la tabla
    nombre = app1.db.Column(app1.db.String(100))
    precio = app1.db.Column(app1.db.Integer)
    stock = app1.db.Column(app1.db.Integer)
    imagen = app1.db.Column(app1.db.String(400))

    def __init__(
        self, nombre, precio, stock, imagen
    ):  # crea el  constructor de la clase
        self.nombre = nombre  # no hace falta el id porque lo crea sola mysql por ser auto_incremento
        self.precio = precio
        self.stock = stock
        self.imagen = imagen
