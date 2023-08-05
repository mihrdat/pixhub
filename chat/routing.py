from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path("ws/<str:index>/", consumers.ChatPageConsumer.as_asgi()),
]
