import pandas as pd
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Dataset, DataColumn, MetabaseConfig, MetabaseDashboard
from .forms import DatasetUploadForm
from .metabase_utils import generate_metabase_url
from .activity_utils import track_activity

@login_required
def dataset_list(request):
    """View to list all datasets owned by the user"""
    # Get user's datasets and public datasets
    user_datasets = Dataset.objects.filter(owner=request.user).order_by('-upload_date')
    public_datasets = Dataset.objects.filter(is_public=True).exclude(owner=request.user).order_by('-upload_date')
    
    return render(request, 'data_manager/dataset_list.html', {
        'user_datasets': user_datasets,
        'public_datasets': public_datasets
    })

@login_required
def dataset_detail(request, pk):
    """View to display dataset details"""
    dataset = get_object_or_404(Dataset, pk=pk)
    
    # Check permissions
    if dataset.owner != request.user and not dataset.is_public:
        messages.error(request, "You don't have permission to view this dataset.")
        return redirect('dataset_list')
    
    # Track this view
    track_activity(request.user, 'VIEW', dataset=dataset)
    
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
    
    # Get associated dashboards
    dashboards = dataset.dashboards.all() if hasattr(dataset, 'dashboards') else []
    
    return render(request, 'data_manager/dataset_detail.html', {
        'dataset': dataset,
        'preview_data': preview_data,
        'dashboards': dashboards
    })

@login_required
def upload_dataset(request):
    """View for uploading dataset files"""
    if request.method == 'POST':
        form = DatasetUploadForm(request.POST, request.FILES)
        if form.is_valid():
            dataset = form.save(commit=False)
            dataset.owner = request.user
            dataset.save()
            
            # Process the uploaded file
            process_dataset_file(dataset)
            
            # Track upload activity
            track_activity(request.user, 'UPLOAD', dataset=dataset)
            
            messages.success(request, f"Dataset '{dataset.name}' uploaded successfully!")
            return redirect('dataset_detail', pk=dataset.pk)
    else:
        form = DatasetUploadForm()
    
    return render(request, 'data_manager/upload.html', {'form': form})

def process_dataset_file(dataset):
    """Extract column information from uploaded file"""
    file_path = dataset.file.path
    
    # Different parsing based on file type
    try:
        if dataset.file_type == 'CSV':
            df = pd.read_csv(file_path)
        elif dataset.file_type == 'EXCEL':
            df = pd.read_excel(file_path)
        elif dataset.file_type == 'JSON':
            df = pd.read_json(file_path)
        else:
            # Default to CSV if file_type is not specified
            df = pd.read_csv(file_path)
        
        # Create column entries for each column in the dataset
        for column in df.columns:
            DataColumn.objects.create(
                dataset=dataset,
                name=column,
                data_type=str(df[column].dtype)
            )
    except Exception as e:
        # Log the error, but don't crash
        print(f"Error processing dataset file: {str(e)}")

@login_required
def view_dashboard(request, pk):
    """View to display an embedded Metabase dashboard"""
    dashboard = get_object_or_404(MetabaseDashboard, pk=pk)
    
    # Check permissions
    if dashboard.dataset.owner != request.user and not dashboard.dataset.is_public:
        messages.error(request, "You don't have permission to view this dashboard.")
        return redirect('dataset_list')
    
    # Track this dashboard view
    track_activity(
        request.user, 
        'DASHBOARD', 
        dataset=dashboard.dataset, 
        dashboard=dashboard
    )
    
    # Get active Metabase config
    try:
        metabase_config = MetabaseConfig.objects.get(is_active=True)
        embed_url = generate_metabase_url(metabase_config, dashboard.dashboard_id)
        metabase_available = True
    except MetabaseConfig.DoesNotExist:
        messages.error(request, "Metabase integration is not configured.")
        metabase_available = False
        embed_url = None
    
    return render(request, 'data_manager/view_dashboard.html', {
        'dashboard': dashboard,
        'embed_url': embed_url,
        'metabase_available': metabase_available
    })

def home(request):
    """View for home page"""
    return render(request, 'data_manager/home.html')

@login_required
def analyze_dataset(request, dataset_id):
    dataset = get_object_or_404(Dataset, pk=dataset_id)
    
    # Check permissions
    if dataset.owner != request.user and not dataset.is_public:
        messages.error(request, "You don't have permission to view this dashboard.")
        return redirect('dataset_list')
    
    # Load the data
    try:
        if dataset.file_type == 'CSV':
            df = pd.read_csv(dataset.file.path)
        elif dataset.file_type == 'EXCEL':
            df = pd.read_excel(dataset.file.path)
        elif dataset.file_type == 'JSON':
            df = pd.read_json(dataset.file.path)
        else:
            # Default to CSV
            df = pd.read_csv(dataset.file.path)
        
        # Basic dataset info
        column_types = {col: str(dtype) for col, dtype in zip(df.columns, df.dtypes)}
        numeric_columns = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
        categorical_columns = df.select_dtypes(include=['object']).columns.tolist()
        
        # Summary statistics for numeric columns
        stats = {}
        for col in numeric_columns:
            stats[col] = {
                'mean': float(df[col].mean()) if not df[col].isnull().all() else 0,
                'min': float(df[col].min()) if not df[col].isnull().all() else 0,
                'max': float(df[col].max()) if not df[col].isnull().all() else 0,
            }
        
        # Prepare data for charts
        chart_data = {}
        
        # For COVID data specifically
        is_covid_data = ('country' in df.columns and 'total_cases' in df.columns)
        
        if is_covid_data:
            # Top countries by cases
            top_cases = df.sort_values('total_cases', ascending=False).head(10)
            chart_data['top_cases'] = {
                'labels': top_cases['country'].tolist(),
                'values': top_cases['total_cases'].tolist()
            }
            
            # Cases vs deaths scatter plot
            if 'total_deaths' in df.columns:
                scatter_data = []
                for _, row in df.iterrows():
                    if pd.notna(row['total_cases']) and pd.notna(row['total_deaths']):
                        scatter_data.append({
                            'x': float(row['total_cases']),
                            'y': float(row['total_deaths']),
                            'country': row['country']
                        })
                
                chart_data['scatter'] = {
                    'data': scatter_data,
                    'x_label': 'Total Cases',
                    'y_label': 'Total Deaths'
                }
            
            # Continent breakdown
            if 'continent' in df.columns:
                continent_data = df.groupby('continent')['total_cases'].sum().sort_values(ascending=False)
                chart_data['continent'] = {
                    'labels': continent_data.index.tolist(),
                    'values': continent_data.values.tolist()
                }
        
        # Generic charts for any dataset
        else:
            # If we have categorical and numeric columns, create bar chart
            if categorical_columns and numeric_columns:
                category_col = categorical_columns[0]  # Use first categorical column
                value_col = numeric_columns[0]  # Use first numeric column
                
                # Get top 10 categories by value
                top_categories = df.groupby(category_col)[value_col].sum().sort_values(ascending=False).head(10)
                
                chart_data['bar'] = {
                    'labels': top_categories.index.tolist(),
                    'values': top_categories.values.tolist(),
                    'category_col': category_col,
                    'value_col': value_col
                }
            
            # If we have multiple numeric columns, create a distribution chart
            if len(numeric_columns) >= 2:
                chart_data['distribution'] = {
                    'labels': numeric_columns[:5],  # First 5 numeric columns
                    'stats': {
                        col: {
                            'min': float(df[col].min()),
                            'q1': float(df[col].quantile(0.25)),
                            'median': float(df[col].median()),
                            'q3': float(df[col].quantile(0.75)),
                            'max': float(df[col].max())
                        } for col in numeric_columns[:5] if not df[col].isnull().all()
                    }
                }
        
        return render(request, 'data_manager/analyze_dataset.html', {
            'dataset': dataset,
            'column_types': column_types,
            'numeric_columns': numeric_columns,
            'categorical_columns': categorical_columns,
            'stats': stats,
            'chart_data': chart_data,
            'is_covid_data': is_covid_data
        })
        
    except Exception as e:
        messages.error(request, f"Error analyzing dataset: {str(e)}")
        return redirect('dataset_detail', pk=dataset_id)