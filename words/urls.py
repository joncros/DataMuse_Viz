from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('wordsets/', views.WordSetListView.as_view(), name='wordsets'),
    path('wordset/<int:pk>', views.WordSetDetailView.as_view(), name='wordset-detail'),
    path('wordset/<int:pk>/delete/', views.WordSetDelete.as_view(), name='wordset_delete'),
    path('wordset/create/', views.WordSetCreate.as_view(), name='wordset_create'),
    path('wordset/create_progress/<int:pk>_<str:job_id>/', views.wordset_create_progress, name='wordset_create_progress'),
    path('wordset/create_json/<str:job_id>/', views.wordset_create_progress_json, name="wordset_create_progress json"),
    path('frequencies/', views.visualization_frequency, name='viz frequency'),
    path('scatterplot/', views.visualization_frequency_scatterplot, name='viz frequency scatterplot'),
    path('related_words/', views.visualization_related_words, name='viz related words'),
]
