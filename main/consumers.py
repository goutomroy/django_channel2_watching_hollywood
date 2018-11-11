import json
from django.core.cache import cache
from channels.generic.http import AsyncHttpConsumer
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage, InvalidPage
from nameparser import HumanName
from rest_framework import status
from utils import app_methods
from main.Serializers import MovieSerializer
from utils.app_methods import verify_firebase_id_token, get_raw_firebase_user, get_user_profile_by_user, \
    delete_from_watchlist, is_movie_in_watchlist, insert_in_watchlist, get_user_profile_by_firebase_uid, \
    create_user_profile, create_new_user, is_user_profile_exists_by_firebase_uid, get_user_by_email, \
    get_or_create_token, is_movie_exists, get_my_watchlist
from utils.app_static_variables import MSG_500, NOW_PLAYING, UPCOMING, POPULAR, \
    MSG_403, MSG_401, MSG_405, MSG_400


class NowPlayingConsumer(AsyncHttpConsumer):
    async def handle(self, body):

        try:
            movies = []
            for page in range(1, 6):
                mvs = cache.get(NOW_PLAYING + '_' + str(page))
                movies.extend(mvs)
            serializer = MovieSerializer(movies, many=True)

            data = json.dumps({'success': True, 'results': serializer.data}).encode()
            return await self.send_response(status.HTTP_200_OK, data, headers=[("Content-Type", "application/json")])

        except Exception as exce:
            data = json.dumps({'message': MSG_500}).encode()
            return await self.send_response(status.HTTP_500_INTERNAL_SERVER_ERROR, data, headers=[("Content-Type", "application/json")])


class UpcomingConsumer(AsyncHttpConsumer):
    async def handle(self, body):

        try:
            movies = []
            for page in range(1, 6):
                mvs = cache.get(UPCOMING + '_' + str(page))
                movies.extend(mvs)
            serializer = MovieSerializer(movies, many=True)

            data = json.dumps({'success': True, 'results': serializer.data}).encode()
            await self.send_response(status.HTTP_200_OK, data, headers=[("Content-Type", "application/json")])

        except Exception as exce:
            data = json.dumps({'message': MSG_500}).encode()
            await self.send_response(status.HTTP_500_INTERNAL_SERVER_ERROR, data, headers=[("Content-Type", "application/json")])


class PopularConsumer(AsyncHttpConsumer):
    async def handle(self, body):
        try:
            movies = []
            for page in range(1, 6):
                mvs = cache.get(POPULAR + '_' + str(page))
                movies.extend(mvs)
            serializer = MovieSerializer(movies, many=True)

            data = json.dumps({'success': True, 'results': serializer.data}).encode()
            return await self.send_response(status.HTTP_200_OK, data, headers=[("Content-Type", "application/json")])

        except Exception as exce:
            data = json.dumps({'message': MSG_500}).encode()
            return await self.send_response(status.HTTP_500_INTERNAL_SERVER_ERROR, data, headers=[("Content-Type", "application/json")])


class SignInConsumer(AsyncHttpConsumer):
    async def handle(self, body):

        if self.scope['method'] != 'POST':
            data = json.dumps({'message': MSG_405}).encode()
            return await self.send_response(status.HTTP_405_METHOD_NOT_ALLOWED, data, headers=[("Content-Type", "application/json")])

        post_data = json.loads(body)
        required_keys = (
            'firebase_id_token',
        )

        if not all(key in post_data for key in required_keys):
            data = json.dumps({'message': MSG_400}).encode()
            return await self.send_response(status.HTTP_400_BAD_REQUEST, data, headers=[("Content-Type", "application/json")])

        firebase_id_token = post_data['firebase_id_token']

        try:

            firebase_uid = await verify_firebase_id_token(firebase_id_token)

            if firebase_uid is None:
                data = json.dumps({'message': MSG_401}).encode()
                return await self.send_response(status.HTTP_401_UNAUTHORIZED, data, headers=[("Content-Type", "application/json")])

            if not await is_user_profile_exists_by_firebase_uid(firebase_uid):

                raw_firebase_user = await get_raw_firebase_user(firebase_uid)
                user = await get_user_by_email(raw_firebase_user.email)
                if user is None:
                    name = HumanName(raw_firebase_user.display_name)
                    username = app_methods.generate_random_username()
                    pass_word = app_methods.generate_random_password()
                    user = await create_new_user(name.first,
                                         (name.middle + ' ' + name.last).strip(),
                                         username,
                                         raw_firebase_user.email,
                                         pass_word)

                user_profile = await create_user_profile(user, firebase_uid)

            else:
                user_profile = await get_user_profile_by_firebase_uid(firebase_uid)
                if user_profile is None:
                    data = json.dumps({'message': MSG_500}).encode()
                    return await self.send_response(status.HTTP_500_INTERNAL_SERVER_ERROR, data, headers=[("Content-Type", "application/json")])

        except Exception as exce:
            data = json.dumps({'message': MSG_500}).encode()
            return await self.send_response(status.HTTP_500_INTERNAL_SERVER_ERROR, data, headers=[("Content-Type", "application/json")])

        token = await get_or_create_token(user_profile.user)

        data = json.dumps({'success': True, 'api_key': token.key}).encode()
        return await self.send_response(status.HTTP_200_OK, data, headers=[("Content-Type", "application/json")])


class WatchlistActionConsumer(AsyncHttpConsumer):
    async def handle(self, body):
        if self.scope['method'] != 'POST':
            data = json.dumps({'message': MSG_405}).encode()
            return await self.send_response(status.HTTP_405_METHOD_NOT_ALLOWED, data, headers=[("Content-Type", "application/json")])

        user = self.scope['user']
        if not user.is_authenticated:
            data = json.dumps({'message': MSG_401}).encode()
            return await self.send_response(status.HTTP_401_UNAUTHORIZED, data, headers=[("Content-Type", "application/json")])

        post_data = json.loads(body)
        required_keys = (
            'movie_id',
            'action_type',
        )

        if not all(key in post_data for key in required_keys):
            data = json.dumps({'message': MSG_400}).encode()
            return await self.send_response(status.HTTP_400_BAD_REQUEST, data, headers=[("Content-Type", "application/json")])

        movie_id = post_data['movie_id']
        action_type = int(post_data['action_type'])

        movie = await is_movie_exists(movie_id)
        if movie is None:
            data = json.dumps({'success': False, 'message': 'Movie Not Found.'}).encode()
            return await self.send_response(status.HTTP_200_OK, data, headers=[("Content-Type", "application/json")])

        user_profile = await get_user_profile_by_user(user)
        if user_profile is None:
            data = json.dumps({'message': MSG_500}).encode()
            return await self.send_response(status.HTTP_500_INTERNAL_SERVER_ERROR, data, headers=[("Content-Type", "application/json")])

        if action_type:

            if await is_movie_in_watchlist(movie, user_profile):
                data = {'success': True, 'message': 'Already in Watchlist'}
            else:
                insert_in_watchlist(movie, user_profile)
                data = {'success': True, 'message': 'Added to watchlist'}
        else:
            if not await is_movie_in_watchlist(movie, user_profile):
                data = {'success': True, 'message': 'Not in Watchlist to remove'}
            else:
                await delete_from_watchlist(movie, user_profile)
                data = {'success': True, 'message': 'Removed from watchlist'}

        data = json.dumps(data).encode()
        return await self.send_response(status.HTTP_200_OK, data, headers=[("Content-Type", "application/json")])


class WatchlistConsumer(AsyncHttpConsumer):
    async def handle(self, body):

        if self.scope['method'] != 'GET':
            data = json.dumps({'message': MSG_405}).encode()
            return await self.send_response(status.HTTP_405_METHOD_NOT_ALLOWED, data, headers=[("Content-Type", "application/json")])

        user = self.scope['user']
        if not user.is_authenticated:
            data = json.dumps({'message': MSG_401}).encode()
            return await self.send_response(status.HTTP_401_UNAUTHORIZED, data, headers=[("Content-Type", "application/json")])

        required_keys = (
            'page',
        )

        from urllib.parse import parse_qs
        params = json.dumps(parse_qs(self.scope['query_string'].decode()))
        params = json.loads(params)
        params = {k: v[0] for k, v in params.items()}

        if not all(key in params for key in required_keys):
            data = json.dumps({'message': MSG_400}).encode()
            return await self.send_response(status.HTTP_400_BAD_REQUEST, data, headers=[("Content-Type", "application/json")])

        page = params['page']

        user_profile = await get_user_profile_by_user(user)
        if user_profile is None:
            data = json.dumps({'message': MSG_500}).encode()
            return await self.send_response(status.HTTP_500_INTERNAL_SERVER_ERROR, data, headers=[("Content-Type", "application/json")])

        my_watchlist = await get_my_watchlist(user_profile)

        data = {}
        items_in_a_page = 10
        paginator = Paginator(my_watchlist, items_in_a_page)
        data['total_results'] = paginator.count
        data['total_pages'] = paginator.num_pages
        data['page'] = page

        try:
            movie_page = paginator.page(page)

            if movie_page.has_previous():
                data['previous'] = movie_page.previous_page_number()
            else:
                # means page=1
                data['previous'] = None

            if movie_page.has_next():
                data['next'] = movie_page.next_page_number()
            else:
                # means page=number_pages
                data['next'] = None

            mvs = []
            for each in movie_page.object_list:
                serializer = MovieSerializer(each.movie)
                mvs.append(serializer.data)

            data['results'] = mvs
            data['success'] = True

            data = json.dumps(data).encode()
            return await self.send_response(status.HTTP_200_OK, data, headers=[("Content-Type", "application/json")])

        except PageNotAnInteger:
            data = json.dumps({'success': False, 'message': 'PageNotAnInteger !'}).encode()
            return await self.send_response(status.HTTP_400_BAD_REQUEST, data, headers=[("Content-Type", "application/json")])

        except EmptyPage:
            data = json.dumps({'success': False, 'message': 'EmptyPage ! No items inserted yet!'}).encode()
            return await self.send_response(status.HTTP_204_NO_CONTENT, data, headers=[("Content-Type", "application/json")])


class DataBuilderConsumer(AsyncHttpConsumer):
    async def handle(self, body):

        if self.scope['method'] != 'GET':
            data = json.dumps({'message': MSG_405}).encode()
            return await self.send_response(status.HTTP_405, data, headers=[("Content-Type", "application/json")])

        user = self.scope['user']
        if not user.is_authenticated:
            data = json.dumps({'message': MSG_401}).encode()
            return await self.send_response(status.HTTP_401_UNAUTHORIZED, data, headers=[("Content-Type", "application/json")])

        if not user.is_superuser:
            data = json.dumps({'message': MSG_403}).encode()
            return await self.send_response(status.HTTP_403_FORBIDDEN, data, headers=[("Content-Type", "application/json")])

        from main.tasks import data_builder
        data_builder.apply_async()
        data = json.dumps({'success': True, 'message': 'ok'}).encode()
        return await self.send_response(status.HTTP_200_OK, data, headers=[("Content-Type", "application/json")])


