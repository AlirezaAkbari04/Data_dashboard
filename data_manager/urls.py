from django.urls import path
from . import views

urlpatterns = [
    path('datasets/', views.dataset_list, name='dataset_list'),
    path('datasets/upload/', views.upload_dataset, name='upload_dataset'),
    path('datasets/<int:pk>/', views.dataset_detail, name='dataset_detail'),
    path('dashboards/<int:pk>/', views.view_dashboard, name='view_dashboard'),
]