import pandas as pd
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Dataset, DataColumn
from .forms import DatasetUploadForm  

@login_required
def upload_dataset(request):
    """View for uploading dataset files"""
    if request.method == 'POST':
        form = DatasetUploadForm(request.POST, request.FILES)
        if form.is_valid():
            dataset = form.save(commit=False)
            dataset.owner = request.user
            dataset.save()
            
            process_dataset_file(dataset)
            
            return redirect('dataset_detail', pk=dataset.pk)
    else:
        form = DatasetUploadForm()
    
    return render(request, 'data_manager/upload.html', {'form': form})

def process_dataset_file(dataset):
    """Extract column information from uploaded file"""
    file_path = dataset.file.path
    
    # Different parsing based on file type
    if dataset.file_type == 'CSV':
        df = pd.read_csv(file_path)
    elif dataset.file_type == 'EXCEL':
        df = pd.read_excel(file_path)
    elif dataset.file_type == 'JSON':
        df = pd.read_json(file_path)
    
    # Create column entries for each column in the dataset
    for column in df.columns:
        DataColumn.objects.create(
            dataset=dataset,
            name=column,
            data_type=str(df[column].dtype)
        )