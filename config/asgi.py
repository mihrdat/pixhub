import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")

application = get_asgi_application()

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
    }
)
