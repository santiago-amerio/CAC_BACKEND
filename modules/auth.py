from datetime import datetime, timedelta


import random
import string

expiration_delay = timedelta(days=60)


def check_user_token(db, User, Token, request):
    token = request["token"]
    user = token.split(".")[0]
    print(user, token)
    # user = Token.query.filter_by(name=user).first()
    result = db.session.query(User, Token).filter_by(name=user).join(User).all()

    for db_user, db_token in result:
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
