from django.urls import path

from . import views

app_name = "chat"

urlpatterns = [
    path("", views.user_list, name="user_list"),
    path("u/<str:username>/", views.chat_view, name="chat"),
    path("message/<int:pk>/delete/", views.delete_message, name="message_delete"),
]

