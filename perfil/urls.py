from django.urls import path
from .views import perfil, selecionar_empresa

urlpatterns = [
    path("", perfil, name="perfil"),
    path("selecionar/<uuid:enterprise_id>/", selecionar_empresa, name="selecionar_empresa"),
]
