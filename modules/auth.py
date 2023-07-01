from datetime import datetime, timedelta
from flask import jsonify,make_response
from collections import defaultdict
import random
import string
from functools import wraps
# tiempo que el token es valido para autenticacion
expiration_delay = timedelta(days=30)


def check_user_token(db, User, Token, request):
    token = request.json["token"]
    user = token.split(".")[0]

    result = db.session.query(User, Token).filter_by(name=user).join(User).all()

    for _, db_token in result:
        if token == db_token.token:
            # si encuentra un token igual al del cliente chequea la expiracion del token
            if datetime.now() - expiration_delay < db_token.creation_date:
                # si el tiempo de ahora menos expiration_delay delta, es menor
                # quiere decir que el token para login sigue vigente, al pasar
                # expiration_delay cantidad de tiempo, el token deja de funcionar
                return True
    # cuando no encuentra un token igual al del del cliente
    # devuelve False
    return False


def login(user, request):
    try:
        print(user.passw == request["passw"] and user.name == request["name"])
        if user.passw == request["passw"] and user.name == request["name"]:
            letters = string.ascii_lowercase
            token = user.name + "." + "".join(random.choice(letters) for i in range(50))

            response = make_response(jsonify({"message": "Login successful"}))
            print("resp",response)
            response.set_cookie("token", token, max_age=expiration_delay.total_seconds(), secure=True)
            print("resp",response)
            return response
        else:
            response = jsonify({"message": "Invalid credentials"})
            response.status_code = 401
            return response
    except:
        response = jsonify({"message": "Error occurred"})
        response.status_code = 500
        return response



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


def needs_auth_decorator(db, User, Token, request):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if check_user_token(db, User, Token, request):
                return func(*args, **kwargs)
            else:
                # Authentication failed, handle accordingly
                return "auth_error"  # or raise an exception

        print(wrapper)
        return wrapper

    return decorator
