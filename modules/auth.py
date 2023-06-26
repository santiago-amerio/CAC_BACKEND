def check_user_token(db, User, Token, request):
    token = request["token"]
    user = token.split(".")[0]
    print(user, token)
    # user = Token.query.filter_by(name=user).first()
    result = db.session.query(User, Token).filter_by(name=user).join(User).all()

    for db_user, db_token in result:
        if token == db_token.token:
            # si encuentra un token igual al del cliente devuelve true
            return True
    # cuando no encuentra un token igual al del del cliente
    # devuelve False
    return False
