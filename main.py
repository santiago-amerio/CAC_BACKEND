#
#   !!! antes que nada corre pip install -r req.txtt !!!
#
from flask import Flask, jsonify, request, render_template


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


#  ************************************************************
class Routes_category(Routes):
    def __init__(self, app):
        self.app = app
        self.routes = [
            {
                "endpoint": "/category",
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

    @needs_auth_decorator(request, required_admin_level=1)
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

    @needs_auth_decorator(request, required_admin_level=1)
    def __patch_category(self):
        json = request.json
        if not "id" in json:
            return {"error": "necesitas la id de la categoria para actualizarla"}
        cat = Category.query.filter_by(id=json["id"]).first()
        
        cat.titulo = json.get("titulo", cat.titulo)
        cat.description = json.get("descripcion", cat.description)
        cat.imagen = json.get("imagen", cat.imagen)
        try:
            db.session.commit()
        except Exception as e:
            print(e)
            return {"error": "categoria ya existe?"}
        print(db.session)
        data = Category.query.get(json["id"])
        dump = category_schema.dump(data)
        return dump

    @needs_auth_decorator(request, required_admin_level=1)
    def __delete_category(self):
        if not "id" in request.json:
            return {"error": "proporciona la id de la categoria a desactivar"}
        category_id = request.json["id"]
        category = Category.query.filter_by(id=category_id).first()
        category.active = False
        try:
            db.session.commit()
        except:
            return {"error": "categoria ya existe?"}
        return category_schema.jsonify(category)


#  ************************************************************
class Routes_user(Routes):
    def __init__(self, app):
        self.app = app
        # super().__init__(app)
        self.routes = [
            {
                "endpoint": "/user",
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

    @needs_auth_decorator(request, required_admin_level=2)
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
    @needs_auth_decorator(request, required_admin_level=2)
    def __post_user(self):
        json = request.json
        required_fields = ["name", "admin_level"]
        missing_fields = [field for field in required_fields if field not in json]
        if missing_fields:
            return {"error": {"missing-fields": missing_fields}}
        name = json["name"]
        admin_level = json["admin_level"]
        passw = auth.generate_password()
        new_user = User(name, passw, admin=admin_level)
        db.session.add(new_user)
        try:
            db.session.commit()
        except:
            return {"error": "Usuario ya registrado?"}
        response = User.query.filter_by(name=name).first()

        return user_schema.jsonify(response)

    @needs_auth_decorator(request, required_admin_level=2)
    def __patch_user(self):
        json = request.json
        if not "id" in json:
            return {"err": "necesitas la id del usuario a modificar"}
        user_id = json["id"]
        user = User.query.filter_by(id=user_id).first()
        user.passw = json.get("passw", user.passw)
        user.name = json.get("name", user.name)
        user.active = json.get("active", user.active)
        user.admin = json.get("admin", user.admin)
        try:
            db.session.commit()
        except:
            return {"error": "error al ingresar datos a la DB"}
        cleared = auth.clear_user_token(db, User, Token, user_id)
        return {"message": "cambios exitosos. " + cleared}

    # cambia la flag active en la base de datos a false
    @needs_auth_decorator(request, required_admin_level=2)
    def __delete_user(self):
        if not "name" in request.json:
            return {
                "error": "proporciona el nombre de la cuenta a desactivar {'nombre':'account-name'}"
            }
        user_name = request.json["user"]
        user = User.query.filter_by(name=user_name).first()
        user.active = False
        try:
            db.session.commit()
        except:
            return {"error": "error al ingresar datos a la DB"}
        return user_schema.jsonify(user)


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
        modelo = request.args.get("modelo")

        if modelo:
            producto = db.session.query(Producto).filter_by(modelo=modelo).first()
            if producto:
                prod_cat = db.session.query(Category).get(producto.categoria)
                serialized_data = producto_schema.dump(producto)
                serialized_data["categoria"] = category_schema.dump(prod_cat)
                return jsonify(serialized_data)

        # Retrieve all products and fetch associated categories
        products = Producto.query.all()
        serialized_products = []
        for product in products:
            prod_cat = db.session.query(Category).get(product.categoria)
            serialized_product = producto_schema.dump(product)
            serialized_product["categoria"] = category_schema.dump(prod_cat)
            serialized_products.append(serialized_product)

        return jsonify(serialized_products)
        # elif "categoria" in json:
        #     response = Producto.query.filter_by(categoria=json["categoria"]).all()
        #     response = productos_schema.dump(response)
        #     return jsonify(response)
        # else:
        #     response = Producto.query.all()
        #     response = productos_schema.dump(response)
        #     return jsonify(response)

    @needs_auth_decorator(request, required_admin_level=1)
    def __post_product(self):
        json = request.json
        required_fields = [
            "modelo",
            "precio",
            "imagen",
            "descripcion",
            "categoria",
            "pb",
            "ccn",
            "pf",
        ]
        missing_fields = [field for field in required_fields if field not in json]

        if missing_fields:
            error = {"err": {"missing-fields": missing_fields}}
            return error
        model = json["modelo"]
        price = json["precio"]
        img = json["imagen"]
        description = json["descripcion"]
        category = json["categoria"]
        pb = json["pb"]
        ccn = json["ccn"]
        pf = json["pf"]
        category_exist = Category.query.filter_by(id=category).first()

        is_in_db = Producto.query.filter_by(modelo=model).first()
        if not category_exist:
            return "la categoria no existe, por favor crea la categoria primero."
        if is_in_db:
            return "producto ya existe."
        new_product = Producto(model, price, img, description, pb, ccn, pf, category)
        db.session.add(new_product)
        try:
            db.session.commit()
        except Exception as e:
            print(e)
            return "Ocurrio un error al insertar en la base de datos"
        response = Producto.query.filter_by(modelo=model).first()

        return producto_schema.jsonify(response)

    @needs_auth_decorator(request, required_admin_level=1)
    def __patch_product(self):
        json = request.json
        required_fields = ["id"]

        missing_fields = [field for field in required_fields if field not in json]
        if missing_fields:
            error = {"err": {"missing-fields": missing_fields}}
            return error
        id = json["id"]
        product = Producto.query.filter_by(id=id).first()
        product.modelo = json.get("modelo", product.modelo)
        product.precio = json.get("precio", product.precio)
        product.imagen = json.get("imagen", product.imagen)
        product.description = json.get("description", product.description)
        product.categoria = json.get("categoria", product.categoria)
        product.pb = json.get("pb", product.pb)
        product.ccn = json.get("ccn", product.ccn)
        product.pf = json.get("pf", product.pf)
        try:
            db.session.commit()
        except Exception as e:
            print(e)
            return "Ocurrio un error al insertar en la base de datos"
        return producto_schema.dump(product)

    @needs_auth_decorator(request, required_admin_level=1)
    def __delete_product(self):
        json = request.json
        required_fields = ["id", "active"]
        missing_fields = [field for field in required_fields if field not in json]
        if missing_fields:
            error = {"err": {"missing-fields": missing_fields}}
            return error
        product = Producto.query.filter_by(id=id).first()
        product.active = json.get("active", product.active)
        try:
            db.session.commit()
        except Exception as e:
            print(e)
            return "Ocurrio un error al insertar en la base de datos"
        return producto_schema.dump(product)


#  ************************************************************
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
                "endpoint": "/",
                "method": ["GET"],
                "function": [self.__get_home_login],
            },
            {
                "endpoint": "/login",
                "method": ["POST"],
                "function": [self.__user_post_login],
            },
            {
                "endpoint": "/user_properties_change",
                "method": ["PATCH"],
                "function": [self.__post_change_client_properties],
            },
            {
                "endpoint": "/register",
                "method": ["POST"],
                "function": [self.__post_register_account],
            },
        ]

        self.register_routes(self.routes)

    def __post_register_account(self):
        json = request.json
        required_fields = ["name", "passw", "mail"]
        missing_fields = [field for field in required_fields if field not in json]
        if missing_fields:
            return {"error": {"missing-fields": missing_fields}}
        name = json["name"]
        passw = json["passw"]
        mail = json["mail"]
        new_client = User(name, passw, mail)
        db.session.add(new_client)
        try:
            db.session.commit()
        except Exception as e:
            print(e)
            return {"error": "Usuario ya registrado?"}
        response = User.query.filter_by(name=name).first()
        return user_schema.jsonify(response)

    def __get_home_login(self):
        return render_template("login.html")

    def __user_post_login(self):
        name = request.json["name"]
        user = User.query.filter_by(name=name).first()

        response, token = auth.login(user, request.json)
        if response.status_code == 200:
            new_token = Token(user.id, token)
            db.session.add(new_token)
            try:
                db.session.commit()
            except:
                return {"error": "error al ingresar datos a la DB"}
            return response
        else:
            return response.json

    @needs_auth_decorator(request)
    def __post_change_client_properties(self):
        user_name = request.cookies["token"].split(".")[0]
        json = request.json
        user = User.query.filter_by(name=user_name).first()
        user.name = json.get("name", user.name)
        user.mail = json.get("mail", user.mail)
        user.passw = json.get("passw", user.passw)
        try:
            db.session.commit()
        except:
            return {"error": "error al ingresar datos a la DB"}
        response = user_schema.dump(user)
        del response["passw"]
        return response

    @needs_auth_decorator(request, required_admin_level=2)
    def __get_clear_tokens(self):
        return auth.clear_timed_out_tokens(db, Token)

    @needs_auth_decorator(request, required_admin_level=1)
    def __post_home(self):
        return instructions_post()

    @needs_auth_decorator(request, required_admin_level=1)
    def __get_home(self):
        return render_template(
            "instructions_template.html", instructions=instructions_post()
        )


#  ************************************************************
# Create the routes
# routes_instance = Routes(app)
routes_product = Routes_product(app)
routes_default = Routes_default(app)
routes_category = Routes_category(app)
routes_user = Routes_user(app)
# routes_client = Routes_client(app)
if __name__ == "__main__":
    app.run(debug=True, port=5000)  # ejecuta el servidor Flask en el puerto 5000
