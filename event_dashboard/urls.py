from django.urls import path, include
from . import views



app_name = 'event_sharer'

urlpatterns = [
    path('', views.index, name="index"),

]



