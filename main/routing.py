from django.urls import path
from main import consumers

http_urlpatterns = [
    path('api/now_playing/', consumers.NowPlayingConsumer),
    path('api/upcoming/', consumers.UpcomingConsumer),
    path('api/popular/', consumers.PopularConsumer),
    path('api/sign_in/', consumers.SignInConsumer),
]
