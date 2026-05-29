"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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

from myproject.auth_service.app.api.views import login_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('myproject.auth_service.app.api.urls')),
    path('api/token/', login_view), # Compatibility for frontend
    path('api/courses/', include('myproject.courses_service.app.api.urls')),
    path('api/ai/', include('myproject.ai_service.app.api.urls')),
    path('api/payments/', include('myproject.payment_service.app.api.urls')),
    path('api/notifications/', include('myproject.notification_service.app.api.urls')),
]

