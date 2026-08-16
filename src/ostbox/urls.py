"""
URL configuration for ostbox project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('devices/', include('apps.devices.urls', namespace='devices')),
    path('components/', include('apps.components.urls', namespace='components')),
]


# Раздача статики и медиа ТОЛЬКО во время разработки
if settings.DEBUG:
    # 1. Раздача медиафайлов (аватарки, документы)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # 2. Раздача статических файлов (CSS, JS, картинки интерфейса)
    # Обычно Django находит статику приложений сам, но для глобальной папки src/static/
    # эта строчка гарантирует, что всё будет работать без сбоев
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
