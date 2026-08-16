from django.urls import path
from . import views

app_name = 'devices'

urlpatterns = [
    path('', views.device_list, name='device-list'),
    path('models/', views.model_list, name='model-list'),
    path('vendors/', views.vendor_list, name='vendor-list'),
]

