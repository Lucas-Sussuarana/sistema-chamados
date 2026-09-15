from django.urls import path
from . import views


urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("abrir/", views.abrir_chamado, name="abrir_chamado"),
    path(
        "chamado/<int:numero>/",
        views.consultar_chamado,
        name="consultar_chamado",
    ),
]