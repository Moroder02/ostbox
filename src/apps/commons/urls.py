from django.urls import path, include

from . import views

app_name = 'commons'

urlpatterns = [
    # Vendors
    path('vendors/', views.vendor_list, name='vendor-list'),
    path('vendor/<int:pk>/', views.vendor_detail, name='vendor-detail'),
    path('vendors/create/', views.vendor_manage, name='vendor-create'),
    path('vendors/<int:pk>/edit/', views.vendor_manage, name='vendor-update'),
    path('vendors/<int:pk>/delete/', views.vendor_delete, name='vendor-delete'),
]
