# project-root/data_manager/models.py
from django.db import models
from django.contrib.auth.models import User

class Dataset(models.Model):
    """Stores uploaded data files"""
    FILE_TYPES = [
        ('CSV', 'CSV File'),
        ('EXCEL', 'Excel File'),
        ('JSON', 'JSON File'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='datasets/')
    file_type = models.CharField(max_length=5, choices=FILE_TYPES)
    upload_date = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.name

class DataColumn(models.Model):
    """Stores information about columns in a dataset"""
    # Make sure the Dataset reference matches exactly
    dataset = models.ForeignKey('Dataset', related_name='columns', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    data_type = models.CharField(max_length=50)
    
    def __str__(self):
        return f"{self.dataset.name} - {self.name}"

class MetabaseConfig(models.Model):
    """Configuration for Metabase integration"""
    site_url = models.URLField(help_text="URL of your Metabase instance")
    secret_key = models.CharField(max_length=100, help_text="Metabase secret key for embedding")
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.site_url
        
class MetabaseDashboard(models.Model):
    """Stores a reference to a Metabase dashboard"""
    # Use string reference for consistency
    dataset = models.ForeignKey('Dataset', on_delete=models.CASCADE, related_name='dashboards')
    dashboard_id = models.IntegerField()
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title