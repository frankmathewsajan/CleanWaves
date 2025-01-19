from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.login, name='login'),
    path('register', views.register, name='register'),
    path('logout', views.logout, name='logout'),

    path('dashboard', views.dashboard, name='dashboard'),
    path('reports', views.reports, name='reports'),
    path('track', views.track, name='track'),
    path('api/region/', views.get_region_points, name='get_region_points'),
    path('api/garbage/', views.garbage_location, name='garbage-location'),
    path('save', views.save_region, name='save'),

    path('u/<str:username>', views.metrics, name='metrics'),

    path('map', views.map, name='map'),
    path('esp_data/', views.esp_data, name='esp_data'),
    path('api/esp_data/', views.get_esp_data, name='get_esp_data'),

]
