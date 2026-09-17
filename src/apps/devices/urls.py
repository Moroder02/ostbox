from django.urls import path, include

from . import views

app_name = 'devices'

urlpatterns = [
    path('', views.device_list, name='device-list'),
    path('kinds/<str:kind>/', views.device_list, name='device-list-by-kinds'),
    path('device/<int:pk>/', views.device_detail, name='device-detail'),

    # Disks
    path('disk-models/', views.disk_model_list, name='disk-model-list'),
    path('disks/', views.disk_list, name='disk-list'),
]
