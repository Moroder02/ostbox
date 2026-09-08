from django.urls import path, include

from . import views

app_name = 'devices'

urlpatterns = [
    path('', views.device_list, name='device-list'),
    path('<str:kind>/', views.device_list, name='device-list-by-kinds'),
    # path('get_devices/', views.get_devices, name='get-devices'),
    # path('dev_list/', views.device_objects_list, name='dev-list'),
]
