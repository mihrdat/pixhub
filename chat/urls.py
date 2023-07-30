from django.urls import path
from . import views

# URLConf
urlpatterns = [
    path("index/", views.index, name="index"),
    path("chat_page/", views.chat_page, name="chat_page"),
]
