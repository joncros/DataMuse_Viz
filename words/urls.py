from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('relations/', views.get_relation_viz, name='relations viz'),  # page for word relationship visualization
]