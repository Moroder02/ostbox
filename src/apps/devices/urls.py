from django.urls import path, include

import apps.devices.views.devices.vendors.views
from . import views

app_name = 'devices'

urlpatterns = [
    path('', views.device_list, name='device-list'),
    path('models/', views.model_list, name='model-list'),

    # Vendors
    path('vendors/', apps.devices.views.devices.vendors.views.vendor_list, name='vendor-list'),
    path('vendor/<int:pk>/', apps.devices.views.devices.vendors.views.vendor_detail, name='vendor-detail'),
    path('vendors/create/', apps.devices.views.devices.vendors.views.vendor_manage, name='vendor-create'),
    path('vendors/<int:pk>/edit/', apps.devices.views.devices.vendors.views.vendor_manage, name='vendor-update'),
    path('vendors/<int:pk>/delete/', apps.devices.views.devices.vendors.views.vendor_delete, name='vendor-delete'),

    path('components/', include('apps.devices.views.components.urls')),

    # # CPU URLs
    # path('cpus/', views.cpu_list, name='cpu-list'),
    # path('cpu-models/', views.cpu_model_list, name='cpu-model-list'),

    # # Disk URLs
    # path('disks/', views.disk_list, name='disk-list'),
    # path('disk-models/', views.disk_model_list, name='disk-model-list'),

    # # RAM URLs
    # path('rams/', views.ram_list, name='ram-list'),
    # path('ram-models/', views.ram_model_list, name='ram-model-list'),

    # # Motherboard URLs
    # path('motherboards/', views.motherboard_list, name='motherboard-list'),
    # path('motherboard-models/', views.motherboard_model_list, name='motherboard-model-list'),
]
