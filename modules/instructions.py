

def instructions_post():
    instructions = {
    "singup": {
        "method": "PUT",
        "options": {
            "name": {
                "type": "string(100)",
                "description": "nombre de usuario",
            },
            "passw": {
                "type": "string(100)",
                "description": "contraseña",
            },
        },
        "returns": {
            "id": {
                "type": "int",
                "description": "database id",
            },
            "name": {
                "type": "string(100)",
                "description": "nombre de usuario",
            },
            "passw": {
                "type": "string(100)",
                "description": "contraseña",
            },
        },
    },
    "login": {
        "method": "POST",
        "options": {
            "name": {
                "type": "string(100)",
                "description": "nombre de usuario",
            },
            "passw": {
                "type": "string(100)",
                "description": "contraseña",
            },
        },
        "returns": {
            "token": {
                "type": "string(150)",
                "description": "token de autenticacion, debe ser enviado con cada peticion que requiera cuenta para ser efectuada",
            }
        },
    }
}

    return instructions
