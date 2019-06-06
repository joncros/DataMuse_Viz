from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('wordsets/', views.WordSetListView.as_view(), name='wordsets'),
    path('wordset/<int:pk>', views.WordSetDetailView.as_view(), name='wordset-detail'),
    path('wordset/<int:pk>/delete/', views.WordSetDelete.as_view(), name='wordset_delete'),
    path('wordset/create/', views.WordSetCreate.as_view(), name='wordset_create'),
    path('frequencies/', views.visualization_frequency, name='viz frequency'),
    path('related_words/', views.visualization_related_words, name='viz related words'),
]
