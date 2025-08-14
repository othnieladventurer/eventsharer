from django.urls import path
from . import views
from .views import CustomSignupView, CustomPasswordResetView



app_name = "users"


urlpatterns = [
    path("accounts/login/", views.custom_login, name="custom_login"),
    path("accounts/signup/", CustomSignupView.as_view(), name="custom_signup"),
    path('logout/', views.custom_logout, name='custom_logout'),
    path('accounts/password/reset/', CustomPasswordResetView.as_view(), name='account_reset_password'),
    path('access-denied/', views.access_denied_view, name='access_denied'),
]







