from django.urls import path, include
from . import views













app_name = 'eventadm'

urlpatterns = [
    path('', views.admin, name="admin"),
    path('plans/', views.subscription_plans, name='plan_list'),
    path('create-checkout-session/', views.create_checkout_session, name='create_checkout_session'),
    path('webhook/', views.stripe_webhook, name='stripe_webhook'),
    path('success/', views.checkout_success, name='checkout_success'),
    path('cancel/', views.checkout_cancel, name='checkout_cancel'),

    path('event/<uuid:uuid>/', views.event_detail, name='event_detail'),
    path('event/<slug:slug>/edit/', views.edit_event, name='event_edit'),
    path('event/<slug:slug>/delete/', views.delete_event, name='delete_event'),

]









