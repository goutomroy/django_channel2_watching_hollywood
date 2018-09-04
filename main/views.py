from django.contrib.auth.models import User
from django.core.cache import cache
from firebase_admin import auth
from nameparser import HumanName
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from main.Serializers import MovieSerializer
from main.models import UserProfile
from watching_hollywood.app_static_methods import verify_firebase_id_token, generate_random_username, \
    generate_random_password
from watching_hollywood.app_static_variables import NOW_PLAYING, UPCOMING, POPULAR, MSG_SOMETHING_WENT_WRONG


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
            return Response({'success': False, 'message': 'Not all required keys are in JSON payload.'})

        firebase_id_token = request.data['firebase_id_token']

        try:

            firebase_uid = verify_firebase_id_token(firebase_id_token)

            if firebase_uid is None:
                return Response({'success': False, 'message': 'Invalid firebase id_token'})

            if not UserProfile.objects.filter(firebase_uid=firebase_uid).exists():

                raw_firebase_user = auth.get_user(firebase_uid)

                if not User.objects.filter(email__iexact=raw_firebase_user.email).exists():
                    user = User.objects.create_user(username=generate_random_username(),
                                                    email=raw_firebase_user.email,
                                                    password=generate_random_password())

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

    @action(methods=['get'], authentication_classes=[TokenAuthentication],
            permission_classes=[IsAuthenticated, IsAdminUser],
            detail=False)
    def start_data_builder(self, request):
        from main.tasks import data_builder
        data_builder.apply_async()
        return Response({'success': True, 'message': 'ok'})
