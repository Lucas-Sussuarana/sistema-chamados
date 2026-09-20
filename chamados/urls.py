from django.urls import path
from . import views


urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("abrir/", views.abrir_chamado, name="abrir_chamado"),

]