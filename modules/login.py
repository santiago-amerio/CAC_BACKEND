import random
import string

def authentication(user,request):
    try:
        if(user.passw == request["passw"]  and user.name == request["name"]):
            letters = string.ascii_lowercase
            token = user.name+"."+''.join(random.choice(letters) for i in range(50))
        
            return token
        else:
            return False
    except:
        return False