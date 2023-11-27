from flight import views
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('base', views.base, name='base'),

    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('Forgot_Password/', views.Forgot_Password, name='Forgot_Password'),
    path('change_password/<token>/', views.change_password, name='change_password'),
    path('logout/', views.logout, name='logout'),

    path('', views.index, name='index'),
    path('flight_result/', views.flight_result, name='flight_result'), 
    path('flight_pricing/', views.flight_pricing, name='flight_pricing'),
    path('Rflight_pricing/', views.Rflight_pricing, name='Rflight_pricing'),
    path('IRflight_pricing/', views.IRflight_pricing, name='IRflight_pricing'),
    path('flight_booking', views.flight_booking, name='flight_booking'),
    path('Rflight_booking', views.Rflight_booking, name='Rflight_booking'),
    path('IRflight_booking', views.IRflight_booking, name='IRflight_booking'),
    path('contact/', views.contact, name='contact'),
    path('create_order/', views.create_order, name='create_order'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)