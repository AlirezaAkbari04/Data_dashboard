from django import forms
from .models import Dataset

class DatasetUploadForm(forms.ModelForm):
    """Form for uploading datasets"""
    class Meta:
        model = Dataset
        fields = ['name', 'description', 'file', 'file_type', 'is_public']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'file_type': forms.Select(attrs={'class': 'form-control'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class DatasetForm(forms.ModelForm):
    """Form for editing datasets"""
    class Meta:
        model = Dataset
        fields = ['name', 'description', 'is_public']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }