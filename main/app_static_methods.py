from channels.db import database_sync_to_async
from django.contrib.auth.models import User
import random
import string
from django.core.cache import cache
from firebase_admin import auth

from main.models import UserProfile


async def get_cache_movies(key):
    return cache.get(key)


@database_sync_to_async
def get_user_profile(user):
    try:
        user_profile = UserProfile.objects.get(user=user)
        return user_profile
    except UserProfile.DoesNotExist:
        return None


async def verify_firebase_id_token(firebase_id_token):
    try:
        from firebase_admin import auth
        decoded_token = auth.verify_id_token(firebase_id_token)
        uid = decoded_token['uid']
    except Exception as exec:
        return None
    return uid


async def get_raw_firebase_user(firebase_uid):
    return auth.get_user(firebase_uid)


@staticmethod
def generate_random_username():
    username = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
    try:
        User.objects.get(username=username)
        return generate_random_username()
    except User.DoesNotExist:
        return username


@staticmethod
def generate_random_password():
    return User.objects.make_random_password(length=8, allowed_chars="abcdefghjkmnpqrstuvwxyz01234567889")


@staticmethod
def print_object(obj):
    from pprint import pprint
    pprint(vars(obj))
