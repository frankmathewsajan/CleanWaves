from django.urls import path
from . import views

urlpatterns = [
    path('data/', views.receive_sensor_data, name='receive_sensor_data'),
    path('data/latest/', views.get_latest_sensor_data, name='get_latest_sensor_data'),
]
