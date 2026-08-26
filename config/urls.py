from django.urls import path

from notify import views

urlpatterns = [
    path("", views.send_form, name="send-form"),
    path("api/send", views.send_api, name="send-api"),
]
