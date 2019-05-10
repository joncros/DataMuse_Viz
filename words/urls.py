from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('relations/', views.get_relation_viz, name='relations viz'),
    path('test_tab/', views.test_tab, name='test tab'),
    path('viz_test/', views.viz_test, name='viz test')
]