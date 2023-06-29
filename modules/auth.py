from datetime import datetime, timedelta
from flask import jsonify
from collections import defaultdict
import random
import string

# tiempo que el token es valido para autenticacion
expiration_delay = timedelta(days=30)


def check_user_token(db, User, Token, request):
    token = request["token"]
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
        if user.passw == request["passw"] and user.name == request["name"]:
            letters = string.ascii_lowercase
            token = user.name + "." + "".join(random.choice(letters) for i in range(50))

            return token
        else:
            return False
    except:
        return False


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


def needs_auth_decorator(
    db,
    User,
    Token,
    request,
):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if check_user_token(db, User, Token, request.json):
                return func(*args, **kwargs)
            else:
                # Authentication failed, handle accordingly
                return "auth_error"  # or raise an exception

        print(wrapper)
        return wrapper

    return decorator
