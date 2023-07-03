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


from modules.db_connection import *


class Routes:
    def __init__(self, app):
        self.app = app

        def __post_init__(self):
            self.initialize_root("root", "changeme")

    def register_routes(self, route_list):
        for route in route_list:
            list_method_funciton = list(
                map(list, list(zip(route["method"], route["function"])))
            )
            for method, function in list_method_funciton:
                self.app.add_url_rule(
                    f"/{route['endpoint']}", view_func=function, methods=[method]
                )


class Routes_category(Routes):
    def __init__(self, app):
        self.app = app
        self.routes = [
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
        ]
        self.register_routes(self.routes)

    def register_routes(self, route_list):
        return super().register_routes(route_list)

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

    @needs_auth_decorator(request)
    def __post_category(self):
        title = request.json["titulo"]
        description = request.json["descripcion"]
        img_url = request.json["imagen"]

        new_category = Category(title, img_url, description)
        db.session.add(new_category)
        try:
            db.session.commit()
        except:
            return {"error": "categoria ya existe?"}
        response = Category.query.filter_by(titulo=title).first()

        return category_schema.jsonify(response)

    def __patch_user(self):
        user_name = request.cookies["token"].split(".")[0]
        user = User.query.filter_by(name=user_name).first()

        if "passw" in request.json:
            user.passw = request.json["passw"]
            db.session.commit()

            cleared = auth.clear_user_token(db, User, Token, user_name)
            return "cambio contraseña " + cleared

        return 'err, necesitas proporcionar un campo "passw" para modificar la contraseña'  # update

    @needs_auth_decorator(request)
    def __patch_category(self):
        json = request.json
        if not "id" in json:
            return {"error": "necesitas la id de la categoria para actualizarla"}
        cat = Category.query.filter_by(id=json["id"])

        if "titulo" in json:
            cat.titulo = json["titulo"]
            print(cat.titulo)

        if "descripcion" in json:
            cat.description = json["descripcion"]

        if "imagen" in json:
            cat.imagen = json["imagen"]

        commit = db.session.commit()
        print(db.session)
        data = Category.query.get(json["id"])
        dump = category_schema.dump(data)
        return dump

    @needs_auth_decorator(request)
    def __delete_category(self):
        if not "id" in request.json:
            return {"error": "proporciona la id de la categoria a desactivar"}
        category_id = request.json["id"]
        category = Category.query.filter_by(id=category_id).first()
        category.active = False
        db.session.commit()
        return category_schema.jsonify(category)


class Routes_user(Routes):
    def __init__(self, app):
        self.app = app
        # super().__init__(app)
        self.routes = [
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
        ]
        self.register_routes(self.routes)

    def register_routes(self, route_list):
        return super().register_routes(route_list)

    @needs_auth_decorator(request, admin=True)
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
    @needs_auth_decorator(request, admin=True)
    def __post_user(self):
        name = request.json["name"]
        passw = auth.generate_password()
        new_user = User(name, passw)
        db.session.add(new_user)
        try:
            db.session.commit()
        except:
            return {"error": "Usuario ya registrado?"}
        response = User.query.filter_by(name=name).first()

        return user_schema.jsonify(response)

    # actualiza contraseña (solo del propio usuario)
    @needs_auth_decorator(request, admin=True)
    def __patch_user(self):
        user_name = request.cookies["token"].split(".")[0]
        user = User.query.filter_by(name=user_name).first()
        print(user.passw)
        if "passw" in request.json:
            user.passw = request.json["passw"]
            db.session.commit()

            cleared = auth.clear_user_token(db, User, Token, user_name)
            return {"message": "cambio contraseña " + cleared}

        return {
            "error": 'necesitas proporcionar un campo "passw" para modificar la contraseña'
        }  # update

    # cambia la flag active en la base de datos a false
    @needs_auth_decorator(request, admin=True)
    def __delete_user(self):
        if not "name" in request.json:
            return {
                "error": "proporciona el nombre de la cuenta a desactivar {'nombre':'account-name'}"
            }
        user_name = request.json["user"]
        user = User.query.filter_by(name=user_name).first()
        user.active = False
        db.session.commit()
        return producto_schema.jsonify(user)


class Routes_product(Routes):
    def __init__(self, app):
        self.app = app
        # super().__init__(app)
        self.routes = [
            {
                "endpoint": "/product",
                "method": ["GET", "POST", "PATCH", "DELETE"],
                "function": [
                    self.__get_product,
                    self.__post_product,
                    self.__patch_product,
                    self.__delete_product,
                ],
            },
        ]
        self.register_routes(self.routes)

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

    @needs_auth_decorator(request, admin=True)
    def __post_product(self):
        json = request.json
        required_fields = ["modelo", "precio", "imagen", "descripcion", "categoria"]
        missing_fields = [field for field in required_fields if field not in json]
        print("faltan campos:" + str(missing_fields))

        if missing_fields:
            error = {"err": "faltan campos:" + str(missing_fields)}
            return error
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

    @needs_auth_decorator(request, admin=True)
    def __patch_product(self):
        return "test"

    @needs_auth_decorator(request, admin=True)
    def __delete_product(self):
        return "test"


class Routes_default(Routes):
    def __init__(self, app):
        self.app = app
        # super().__init__(app)
        self.routes = [
            {
                "endpoint": "/clear_tokens",
                "method": ["GET"],
                "function": [
                    self.__get_clear_tokens,
                ],
            },
            {
                "endpoint": "/admin",
                "method": ["GET", "POST"],
                "function": [self.__get_home, self.__post_home],
            },
            {
                "endpoint": "/",
                "method": ["GET"],
                "function": [self.__get_home_login],
            },
            {
                "endpoint": "login",
                "method": ["POST"],
                "function": [
                    self.__post_login,
                ],
            },
        ]
        # self.app.add_url_rule("/", view_func=self.__post_home, methods=["POST"])
        # self.app.add_url_rule("/", view_func=self.__get_home, methods=["GET"])
        self.register_routes(self.routes)

    def __get_home_login(self):
        return render_template("login.html")

    def __post_login(self):
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

    @needs_auth_decorator(request, admin=True)
    def __get_clear_tokens(self):
        return auth.clear_timed_out_tokens(db, Token)

    @needs_auth_decorator(request, admin=True)
    def __post_home(self):
        return instructions_post()

    @needs_auth_decorator(request, admin=True)
    def __get_home(self):
        return render_template(
            "instructions_template.html", instructions=instructions_post()
        )


class Routes_client:
    def __init__():
        return


# Create the routes
# routes_instance = Routes(app)
routes_user = Routes_user(app)
routes_product = Routes_product(app)
routes_default = Routes_default(app)
routes_category = Routes_category(app)
if __name__ == "__main__":
    app.run(debug=True, port=5000)  # ejecuta el servidor Flask en el puerto 5000
