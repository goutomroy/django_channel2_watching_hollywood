import asyncio
import json

from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from django.core.cache import cache
from channels.generic.http import AsyncHttpConsumer
from nameparser import HumanName
from rest_framework.authtoken.models import Token

from main import app_static_methods
from main.Serializers import MovieSerializer
from main.app_static_methods import verify_firebase_id_token, get_raw_firebase_user
from main.app_static_variables import MSG_SOMETHING_WENT_WRONG, NOW_PLAYING, UPCOMING, POPULAR, MSG_NOT_ALL_KEYS
from main.models import UserProfile


class NowPlayingConsumer(AsyncHttpConsumer):
    async def handle(self, body):

        try:
            movies = []
            for page in range(1, 6):
                mvs = cache.get(NOW_PLAYING + '_' + str(page))
                movies.extend(mvs)
            serializer = MovieSerializer(movies, many=True)

            data = json.dumps({'success': True, 'results': serializer.data}).encode()
            await self.send_response(200, data, headers=[("Content-Type", "application/json")])

        except Exception as exce:
            data = json.dumps({'success': False, 'message': MSG_SOMETHING_WENT_WRONG}).encode()
            await self.send_response(200, data, headers=[("Content-Type", "application/json")])


class UpcomingConsumer(AsyncHttpConsumer):
    async def handle(self, body):

        try:
            movies = []
            for page in range(1, 6):
                mvs = cache.get(UPCOMING + '_' + str(page))
                movies.extend(mvs)
            serializer = MovieSerializer(movies, many=True)

            data = json.dumps({'success': True, 'results': serializer.data}).encode()
            await self.send_response(200, data, headers=[("Content-Type", "application/json")])

        except Exception as exce:
            data = json.dumps({'success': False, 'message': MSG_SOMETHING_WENT_WRONG}).encode()
            await self.send_response(200, data, headers=[("Content-Type", "application/json")])


class PopularConsumer(AsyncHttpConsumer):
    async def handle(self, body):
        try:
            movies = []
            for page in range(1, 6):
                mvs = cache.get(POPULAR + '_' + str(page))
                movies.extend(mvs)
            serializer = MovieSerializer(movies, many=True)

            data = json.dumps({'success': True, 'results': serializer.data}).encode()
            return await self.send_response(200, data, headers=[("Content-Type", "application/json")])

        except Exception as exce:
            data = json.dumps({'success': False, 'message': MSG_SOMETHING_WENT_WRONG}).encode()
            return await self.send_response(200, data, headers=[("Content-Type", "application/json")])


class SignInConsumer(AsyncHttpConsumer):
    async def handle(self, body):

        if self.scope['method'] != 'POST':
            data = json.dumps({'message': 'Request method is not allowed'}).encode()
            return await self.send_response(405, data, headers=[("Content-Type", "application/json")])

        post_data = json.loads(body)
        required_keys = (
            'firebase_id_token',
        )

        if not all(key in post_data for key in required_keys):
            data = json.dumps({'message': MSG_NOT_ALL_KEYS}).encode()
            return await self.send_response(400, data, headers=[("Content-Type", "application/json")])

        firebase_id_token = post_data['firebase_id_token']

        try:

            firebase_uid = await verify_firebase_id_token(firebase_id_token)

            if firebase_uid is None:
                data = json.dumps({'success': False, 'message': 'Invalid firebase id_token'}).encode()
                return await self.send_response(200, data, headers=[("Content-Type", "application/json")])

            if not await self.is_user_profile_exists(firebase_uid):

                raw_firebase_user = await get_raw_firebase_user(firebase_uid)
                user = await self.get_user_by_email(raw_firebase_user.email)
                if user is None:
                    name = HumanName(raw_firebase_user.display_name)
                    username = app_static_methods.generate_random_username()
                    pass_word = app_static_methods.generate_random_password()
                    user = await self.create_new_user(name.first,
                                         (name.middle + ' ' + name.last).strip(),
                                         username,
                                         raw_firebase_user.email,
                                         pass_word)

                user_profile = await self.create_user_profile(user, firebase_uid)

            else:
                user_profile = await self.get_user_profile(firebase_uid)
                if user_profile is None:
                    data = json.dumps({'success': False, 'message': MSG_SOMETHING_WENT_WRONG}).encode()
                    return await self.send_response(200, data, headers=[("Content-Type", "application/json")])

        except Exception as exce:
            data = json.dumps({'success': False, 'message': MSG_SOMETHING_WENT_WRONG}).encode()
            return await self.send_response(200, data, headers=[("Content-Type", "application/json")])

        token = await self.get_or_create_token(user_profile.user)

        data = {
            'api_key': token.key,
        }

        data = json.dumps({'success': True, 'details': {'basic': data}}).encode()
        return await self.send_response(200, data, headers=[("Content-Type", "application/json")])

    @database_sync_to_async
    def create_new_user(self, first_name, last_name, username, email, password):
        return User.objects.create_user(first_name=first_name,
                                        last_name=last_name,
                                        username=username,
                                        email=email,
                                        password=password)

    @database_sync_to_async
    def is_user_profile_exists(self, firebase_uid):
        return UserProfile.objects.filter(firebase_uid=firebase_uid).exists()

    @database_sync_to_async
    def create_user_profile(self, user, firebase_uid):
        return UserProfile.objects.create(user=user, firebase_uid=firebase_uid)

    @database_sync_to_async
    def get_user_profile(self, firebase_uid):
        try:
            user_profile = UserProfile.objects.get(firebase_uid=firebase_uid)
            return user_profile
        except UserProfile.DoesNotExist:
            return None

    @database_sync_to_async
    def get_user_by_email(self, email):
        try:
            user = User.objects.get(email__iexact=email)
            return user
        except User.DoesNotExist:
            return None

    @database_sync_to_async
    def get_or_create_token(self, user):
        token = Token.objects.get_or_create(user=user)
        return token
