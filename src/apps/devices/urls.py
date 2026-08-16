from django.urls import path, include

from . import views

app_name = 'devices'

urlpatterns = [
    path('', views.device_list, name='device-list'),
    path('models/', views.model_list, name='model-list'),

    # Vendors
    path('vendors/', views.vendor_list, name='vendor-list'),
    path('vendor/<int:pk>/', views.vendor_detail, name='vendor-detail'),
    path('vendors/create/', views.vendor_manage, name='vendor-create'),
    path('vendors/<int:pk>/edit/', views.vendor_manage, name='vendor-update'),
    path('vendors/<int:pk>/delete/', views.vendor_delete, name='vendor-delete'),

    # CPU URLs
    path('components/cpus/', views.cpu_list, name='cpu-list'),
    path('components/cpu-models/', views.cpu_model_list, name='cpu-model-list'),

    # Disk URLs
    path('components/disks/', views.disk_list, name='disk-list'),
    path('components/disk-models/', views.disk_model_list, name='disk-model-list'),

    # RAM URLs
    path('components/rams/', views.ram_list, name='ram-list'),
    path('components/ram-models/', views.ram_model_list, name='ram-model-list'),

    # Motherboard URLs
    path('components/motherboards/', views.motherboard_list, name='motherboard-list'),
    path('components/motherboard-models/', views.motherboard_model_list, name='motherboard-model-list'),
]
