from channels.http import AsgiHandler
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path, re_path
from main import consumers
from utils.token_auth_middleware import TokenAuthMiddleware

application = ProtocolTypeRouter({

    'http': TokenAuthMiddleware(
        URLRouter(
            [
                path('api/now_playing/', consumers.NowPlayingConsumer),
                path('api/upcoming/', consumers.UpcomingConsumer),
                path('api/popular/', consumers.PopularConsumer),
                path('api/sign_in/', consumers.SignInConsumer),
                path('api/watchlist_action/', consumers.WatchlistActionConsumer),
                path('api/watchlist/', consumers.WatchlistConsumer),
                path('api/start_data_builder/', consumers.DataBuilderConsumer),
                re_path("^", AsgiHandler),
            ]
        )
    ),

})

