import pandas as pd
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Dataset, DataColumn, MetabaseConfig, MetabaseDashboard
from .forms import DatasetUploadForm
from .metabase_utils import generate_metabase_url

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
            
            messages.success(request, f"Dataset '{dataset.name}' uploaded successfully!")
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

@login_required
def dataset_detail(request, pk):
    """View to display dataset details"""
    dataset = Dataset.objects.get(pk=pk)
    
    # Only show preview if the user owns this dataset
    if dataset.owner != request.user:
        messages.error(request, "You don't have permission to view this dataset.")
        return redirect('dataset_list')
    
    # Load the data for preview
    preview_data = None
    try:
        if dataset.file_type == 'CSV':
            df = pd.read_csv(dataset.file.path)
        elif dataset.file_type == 'EXCEL':
            df = pd.read_excel(dataset.file.path)
        elif dataset.file_type == 'JSON':
            df = pd.read_json(dataset.file.path)
        
        # Get a preview of the first 10 rows
        preview_data = {
            'columns': df.columns.tolist(),
            'rows': df.head(10).values.tolist(),
            'total_rows': len(df)
        }
    except Exception as e:
        messages.error(request, f"Error loading data preview: {str(e)}")
    
    return render(request, 'data_manager/dataset_detail.html', {
        'dataset': dataset,
        'preview_data': preview_data
    })

@login_required
def dataset_list(request):
    """View to list all datasets owned by the user"""
    datasets = Dataset.objects.filter(owner=request.user).order_by('-created_at')
    return render(request, 'data_manager/dataset_list.html', {'datasets': datasets})

@login_required
def view_dashboard(request, pk):
    """View to display an embedded Metabase dashboard"""
    dashboard = MetabaseDashboard.objects.get(pk=pk)
    
    # Check permissions
    if dashboard.dataset.owner != request.user:
        messages.error(request, "You don't have permission to view this dashboard.")
        return redirect('dataset_list')
    
    # Get active Metabase config
    try:
        metabase_config = MetabaseConfig.objects.get(is_active=True)
    except MetabaseConfig.DoesNotExist:
        messages.error(request, "Metabase integration is not configured.")
        return redirect('dataset_detail', pk=dashboard.dataset.pk)
    
    # Generate embedded URL
    embed_url = generate_metabase_url(metabase_config, dashboard.dashboard_id)
    
    return render(request, 'data_manager/view_dashboard.html', {
        'dashboard': dashboard,
        'embed_url': embed_url
    })