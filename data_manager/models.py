# data_manager/models.py
from django.db import models
from django.contrib.auth.models import User

class Dataset(models.Model):
    """Stores uploaded data files"""
    # Choices are defined as tuples (stored_value, display_value)
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
    """Stores individual data points from datasets"""
    dataset = models.ForeignKey(Dataset, related_name='columns', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    data_type = models.CharField(max_length=50)
    
    def __str__(self):
        return f"{self.dataset.name} - {self.value}"