from django import forms
from .models import Dataset

class DatasetUploadForm(forms.ModelForm):
    """Form for uploading datasets"""
    class Meta:
        model = Dataset
        fields = ['name', 'description', 'file', 'file_type']

class DatasetUploadForm(forms.ModelForm):
    class Meta:
        model = Dataset
        fields = ['name', 'description', 'file', 'file_type']