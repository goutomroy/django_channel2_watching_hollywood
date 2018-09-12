from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

from main import routing

application = ProtocolTypeRouter({

    'http': AuthMiddlewareStack(
        URLRouter(
            routing.http_urlpatterns
        )
    ),
})

