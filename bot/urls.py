from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.login, name='login'),
    path('register', views.register, name='register'),
    path('logout', views.logout, name='logout'),

    path('dashboard', views.dashboard, name='dashboard'),
    path('reports', views.reports, name='reports'),

    path('u/<str:username>', views.metrics, name='metrics'),

]


