from django.urls import path
from .views import register_view, login_view, me_view, google_login, microsoft_login

urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('me/', me_view, name='me'),
    path('google-login/', google_login, name='google_login'),
    path('microsoft-login/', microsoft_login, name='microsoft_login'),
]
