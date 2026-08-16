from django.urls import path
from . import views

app_name = 'components'

urlpatterns = [
    # CPU URLs
    path('cpus/', views.cpu_list, name='cpu-list'),
    path('cpu-models/', views.cpu_model_list, name='cpu-model-list'),

    # Disk URLs
    path('disks/', views.disk_list, name='disk-list'),
    path('disk-models/', views.disk_model_list, name='disk-model-list'),

    # RAM URLs
    path('rams/', views.ram_list, name='ram-list'),
    path('ram-models/', views.ram_model_list, name='ram-model-list'),

    # Motherboard URLs
    path('motherboards/', views.motherboard_list, name='motherboard-list'),
    path('motherboard-models/', views.motherboard_model_list, name='motherboard-model-list'),
]
