from django.urls import path
from . import views

# URLConf
urlpatterns = [
    path("chat_page/", views.chat_page, name="chat_page"),
]
