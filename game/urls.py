from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("create/", views.create_room, name="create_room"),
    path("r/<str:code>/", views.handoff, name="handoff"),
    path("r/<str:code>/reveal/", views.reveal, name="reveal"),
    path("r/<str:code>/next/", views.next_player, name="next_player"),
    path("r/<str:code>/done/", views.done, name="done"),
]
