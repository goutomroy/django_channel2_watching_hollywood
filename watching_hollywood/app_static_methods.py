from django.contrib.auth.models import User
import random
import string

def generate_random_username():
    username = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
    try:
        User.objects.get(username=username)
        return generate_random_username()
    except User.DoesNotExist:
        return username


def generate_random_password():
    return User.objects.make_random_password(length=8, allowed_chars="abcdefghjkmnpqrstuvwxyz01234567889")


def verify_firebase_id_token(firebase_id_token):
    try:
        from firebase_admin import auth
        decoded_token = auth.verify_id_token(firebase_id_token)
        uid = decoded_token['uid']
    except Exception as exec:
        print(exec)
        return None
    return uid


def print_object(obj):
    from pprint import pprint
    pprint(vars(obj))
