from channels.db import database_sync_to_async
from django.contrib.auth.models import User
import random
import string
from django.core.cache import cache
from firebase_admin import auth
from rest_framework.authtoken.models import Token
from main.models import UserProfile, Movie, Watchlist


@database_sync_to_async
def create_new_user(first_name, last_name, username, email, password):
    return User.objects.create_user(first_name=first_name,
                                    last_name=last_name,
                                    username=username,
                                    email=email,
                                    password=password)


@database_sync_to_async
def is_user_profile_exists_by_firebase_uid(firebase_uid):
    return UserProfile.objects.filter(firebase_uid=firebase_uid).exists()


@database_sync_to_async
def create_user_profile(user, firebase_uid):
    return UserProfile.objects.create(user=user, firebase_uid=firebase_uid)


@database_sync_to_async
def get_my_watchlist(user_profile):
    return Watchlist.objects.filter(user_profile=user_profile).order_by('-created')


@database_sync_to_async
def get_user_profile_by_firebase_uid(firebase_uid):
    try:
        user_profile = UserProfile.objects.get(firebase_uid=firebase_uid)
        return user_profile
    except UserProfile.DoesNotExist:
        return None


@database_sync_to_async
def get_user_by_email(email):
    try:
        user = User.objects.get(email__iexact=email)
        return user
    except User.DoesNotExist:
        return None


@database_sync_to_async
def get_or_create_token(user):
    token = Token.objects.get_or_create(user=user)
    return token


@database_sync_to_async
def get_user_profile_by_user(user):
    try:
        user_profile = UserProfile.objects.get(user=user)
        return user_profile
    except UserProfile.DoesNotExist:
        return None


@database_sync_to_async
def is_movie_exists(movie_id):
    try:
        movie = Movie.objects.get(id=movie_id)
        return movie
    except Movie.DoesNotExist:
        return None


@database_sync_to_async
def is_movie_in_watchlist(movie, user_profile):
    return Watchlist.objects.filter(movie=movie, user_profile=user_profile).exists()


@database_sync_to_async
def insert_in_watchlist(movie, user_profile):
    return Watchlist.objects.create(movie=movie, user_profile=user_profile)


async def get_cache_movies(key):
    return cache.get(key)

@database_sync_to_async
def delete_from_watchlist(movie, user_profile):
    return Watchlist.objects.delete(movie=movie, user_profile=user_profile)


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
