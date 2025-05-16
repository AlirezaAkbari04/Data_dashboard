from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('datasets/', views.dataset_list, name='dataset_list'),
    path('accounts/', include('django.contrib.auth.urls')),  
    path('datasets/upload/', views.upload_dataset, name='upload_dataset'),
    path('datasets/<int:pk>/', views.dataset_detail, name='dataset_detail'),
    path('datasets/<int:dataset_id>/analyze/', views.analyze_dataset, name='analyze_dataset'),
    path('dashboards/<int:pk>/', views.view_dashboard, name='view_dashboard'),
]   + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)