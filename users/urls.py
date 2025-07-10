from django.urls import path
from . import views




app_name = "users"


urlpatterns = [
    path("accounts/login/", views.custom_login, name="account_login"),
    path('logout/', views.custom_logout, name='custom_logout'),
    path('access-denied/', views.access_denied_view, name='access_denied'),
]







