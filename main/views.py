from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from firebase_admin import auth
from nameparser import HumanName
from rest_framework import viewsets, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from main.Serializers import MovieSerializer, WatchlistSerializer
from main.models import UserProfile, Movie, Watchlist
from watching_hollywood import app_static_methods
from watching_hollywood.app_static_variables import NOW_PLAYING, UPCOMING, POPULAR, MSG_SOMETHING_WENT_WRONG, \
    MSG_NOT_ALL_KEYS


class MainViewSet(viewsets.GenericViewSet):

    @action(methods=['get'], permission_classes=[AllowAny], detail=False)
    def now_playing(self, request):

        try:
            movies = []
            for page in range(1, 6):
                movies.extend(cache.get(NOW_PLAYING+'_'+str(page)))
            serializer = MovieSerializer(movies, many=True)
            return Response({'success': True, 'results': serializer.data})

        except Exception as exce:
            return Response({'success': False, 'message': MSG_SOMETHING_WENT_WRONG})

    @action(methods=['get'], permission_classes=[AllowAny], detail=False)
    def upcoming(self, request):

        try:
            movies = []
            for page in range(1, 6):
                movies.extend(cache.get(UPCOMING+'_'+str(page)))
            serializer = MovieSerializer(movies, many=True)
            return Response({'success': True, 'results': serializer.data})

        except Exception as exce:
            return Response({'success': False, 'message': MSG_SOMETHING_WENT_WRONG})

    @action(methods=['get'], permission_classes=[AllowAny], detail=False)
    def popular(self, request):

        try:
            movies = []
            for page in range(1, 6):
                movies.extend(cache.get(POPULAR+'_'+str(page)))
            serializer = MovieSerializer(movies, many=True)
            return Response({'success': True, 'results': serializer.data})

        except Exception as exce:
            return Response({'success': False, 'message': MSG_SOMETHING_WENT_WRONG})

    @action(methods=['post'],
            detail=False)
    def sign_in(self, request):
        required_keys = (
            'firebase_id_token',
        )

        if not all(key in request.data for key in required_keys):
            return Response({'success': False, 'message': MSG_NOT_ALL_KEYS})

        firebase_id_token = request.data['firebase_id_token']

        try:

            firebase_uid = app_static_methods.verify_firebase_id_token(firebase_id_token)

            if firebase_uid is None:
                return Response({'success': False, 'message': 'Invalid firebase id_token'})

            if not UserProfile.objects.filter(firebase_uid=firebase_uid).exists():

                raw_firebase_user = auth.get_user(firebase_uid)

                if not User.objects.filter(email__iexact=raw_firebase_user.email).exists():
                    user = User.objects.create_user(username=app_static_methods.generate_random_username(),
                                                    email=raw_firebase_user.email,
                                                    password=app_static_methods.generate_random_password())

                    name = HumanName(raw_firebase_user.display_name)
                    user.first_name = name.first
                    user.last_name = (name.middle + ' ' + name.last).strip()
                    user.save()
                else:
                    user = User.objects.get(email__iexact=raw_firebase_user.email)

                if not Token.objects.filter(user=user).exists():
                    Token.objects.create(user=user)

                user_profile = UserProfile.objects.create(user=user, firebase_uid=firebase_uid)

            else:
                user_profile = UserProfile.objects.get(firebase_uid=firebase_uid)

        except Exception as exce:
            return Response({'success': False, 'message': MSG_SOMETHING_WENT_WRONG})

        token = Token.objects.get(user=user_profile.user)
        data = {
            'api_key': token.key,
        }

        return Response({'success': True, 'details': {'basic': data}})

    @action(methods=['post'], authentication_classes=[TokenAuthentication],
            permission_classes=[IsAuthenticated], detail=False)
    def watchlist_action(self, request):
        user_profile = UserProfile.objects.get(user=request.user)

        required_keys = (
            'movie_id',
            'action_type',
        )

        if not all(key in request.POST for key in required_keys):
            return Response({'success': False, 'message': MSG_NOT_ALL_KEYS})

        movie_id = request.POST.get('movie_id')
        action_type = int(request.POST.get('action_type'))

        try:
            movie = Movie.objects.get(id=movie_id)
        except Movie.DoesNotExist:
            return Response({'success': False, 'message': 'Movie Not Found.'})

        if action_type:

            if Watchlist.objects.filter(movie=movie, user_profile=user_profile).exists():
                data = {'success': True, 'message': 'already in Watchlist'}
            else:
                Watchlist.objects.create(movie=movie, user_profile=user_profile)
                data = {'success': True, 'message': 'added to watchlist'}
        else:
            if not Watchlist.objects.filter(movie=movie, user_profile=user_profile).exists():
                data = {'success': True, 'message': 'already not in Watchlist'}
            else:
                Watchlist.objects.delete(movie=movie, user_profile=user_profile)
                data = {'success': True, 'message': 'removed from watchlist'}

        return Response(data)

    @action(methods=['get'], authentication_classes=[TokenAuthentication],
            permission_classes=[IsAuthenticated], detail=False)
    def watchlist(self, request):
        user_profile = UserProfile.objects.get(user=request.user)

        required_keys = (
            'page',
        )

        if not all(key in request.GET for key in required_keys):
            return Response({'success': False, 'message': MSG_NOT_ALL_KEYS})

        page = request.GET.get('page')

        my_watchlist = Watchlist.objects.filter(user_profile=user_profile).order_by('-created')

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

            serializer = WatchlistSerializer(movie_page.object_list, many=True)

            data['results'] = serializer.data
            data['success'] = True

        except PageNotAnInteger:
            # If page is not an integer(e.g. 3b, n, c2).
            message = {'success': False, 'message': 'PageNotAnInteger !'}
            return Response(data=message, status=status.HTTP_400_BAD_REQUEST)

        except EmptyPage:
            # If page is out of range or less than 1
            message = {'success': False, 'message': 'EmptyPage ! No items inserted yet!'}
            return Response(data=message, status=status.HTTP_204_NO_CONTENT)

        return Response(data=data)

    @action(methods=['get'], authentication_classes=[TokenAuthentication],
            permission_classes=[IsAuthenticated, IsAdminUser],
            detail=False)
    def start_data_builder(self, request):
        from main.tasks import data_builder
        data_builder.apply_async()
        return Response({'success': True, 'message': 'ok'})
