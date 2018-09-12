from channels.auth import AuthMiddlewareStack
from channels.http import AsgiHandler
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path, re_path

from main import consumers
from watching_hollywood.token_auth_middleware import TokenAuthMiddleware

application = ProtocolTypeRouter({

    'http': TokenAuthMiddleware(
        URLRouter(
            [
                path('api/now_playing/', consumers.NowPlayingConsumer),
                path('api/upcoming/', consumers.UpcomingConsumer),
                path('api/popular/', consumers.PopularConsumer),
                path('api/sign_in/', consumers.SignInConsumer),
                path('api/watchlist_action/', consumers.WatchlistActionConsumer),
                re_path("^", AsgiHandler),
            ]
        )
    ),

})

