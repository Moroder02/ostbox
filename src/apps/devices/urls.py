from django.urls import path, include

from . import views

app_name = 'devices'

urlpatterns = [
    path('', views.device_list, name='device-list'),
    path('get_devices/', views.get_devices, name='get-devices'),
]
