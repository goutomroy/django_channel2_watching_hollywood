from django.core.cache import cache
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from main.Serializers import MovieSerializer
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

    @action(methods=['get'], authentication_classes=[TokenAuthentication],
            permission_classes=[IsAuthenticated, IsAdminUser],
            detail=False)
    def start_data_builder(self, request):
        from main.tasks import data_builder
        data_builder.apply_async()
        return Response({'success': True, 'message': 'ok'})
