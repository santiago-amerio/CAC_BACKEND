from datetime import datetime, timedelta
from flask import jsonify, make_response
from collections import defaultdict
import random
import string
from functools import wraps

from modules.db_connection import db, User, Token


# tiempo que el token es valido para autenticacion
expiration_delay = timedelta(days=30)


def check_user_token(request):
    token = request.cookies["token"]
    user = token.split(".")[0]
    result = db.session.query(User, Token).filter_by(name=user).join(User).all()

    for db_user, db_token in result:
        if token == db_token.token:
            # si encuentra un token igual al del cliente chequea la expiracion del token
            if datetime.now() - expiration_delay < db_token.creation_date:
                # si el tiempo de ahora menos expiration_delay delta, es menor
                # quiere decir que el token para login sigue vigente, al pasar
                # expiration_delay cantidad de tiempo, el token deja de funcionar
                return (True, db_user.admin)
    # cuando no encuentra un token igual al del del cliente
    # devuelve False
    return (False, False)


def login(user, request):
    try:
        if (
            user.passw == request["passw"]
            and user.name == request["name"]
            and user.active
        ):
            letters = string.ascii_lowercase
            token = user.name + "." + "".join(random.choice(letters) for i in range(50))

            response = make_response(jsonify({"message": "Login successful"}))

            response.set_cookie(
                "token", token, max_age=expiration_delay.total_seconds(), secure=True
            )
            response.set_cookie(
                "is_admin",
                str(user.admin),
                max_age=expiration_delay.total_seconds(),
                secure=True,
            )
            return (response, token)
        else:
            response = jsonify({"error": "Invalid credentials"})
            response.status_code = 401
            return (response, user.name)
    except Exception as e:
        print(e)
        response = jsonify({"error": "Error occurred,falta usuario?"})
        response.status_code = 500
        return (response, "user.name")


def clear_timed_out_tokens(db, Token):
    # esta funcion elimina los tokens expirados de la tabla de tokens
    all_tokens = Token.query.all()
    cleared_tokens = {
        "had_expired_tokens": False,
        "total_tokens_cleared": 0,
        "accounts": defaultdict(int),
    }
    for token in all_tokens:
        if datetime.now() - expiration_delay > token.creation_date:
            cleared_tokens["had_expired_tokens"] = True
            cleared_tokens["total_tokens_cleared"] += 1
            cleared_tokens["accounts"][token.user_id] += 1
            producto = Token.query.get(token.id)
            db.session.delete(producto)
            db.session.commit()
    cleared_tokens["accounts"] = dict(cleared_tokens["accounts"])
    return cleared_tokens


def needs_auth_decorator(request, required_admin_level=0):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if "token" not in request.cookies:
                return {"error": ' cookie "token" no encontrada, iniciaste sesion? '}

            authenticated, admin_level = check_user_token(request)
            if authenticated:
                if required_admin_level <= admin_level:
                    return func(*args, **kwargs)

                else:
                    return {"error": "permisos_insuficientes"}
            else:
                # Authentication failed
                return {"error": "auth_error"}

        return wrapper

    return decorator


def clear_user_token(db, User, Token, user_id):
    user = User.query.filter_by(id=user_id).first()
    print(user)
    if user:
        Token.query.filter_by(user_id=user.id).delete()
        db.session.commit()
        return "tokens eliminados"
    return "token remover error"


def generate_password():
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for i in range(10))
