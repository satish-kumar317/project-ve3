
from django.shortcuts import render
import pandas as pd
import numpy as np
from .forms import UploadFileform
import os
from django.core.files.storage import FileSystemStorage
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import matplotlib
matplotlib.use('Agg')
#create your views
def handle_uploaded_file(file):
    file_storage = FileSystemStorage()
    filename = file_storage.save(file.name, file)
    file_path = file_storage.path(filename)
    return file_path

def save_plot_to_base64(plt):
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    return base64.b64encode(image_png).decode('utf-8')

def generate_histogram(series, column_name):
    plt.figure()
    series.hist(bins=30, alpha=0.75, color='blue', edgecolor='black')
    plt.title(f'Histogram of {column_name}')
    plt.xlabel(column_name)
    plt.ylabel('Frequency')
    return save_plot_to_base64(plt)

def upload_file(request):
    if request.method == 'POST':
        form = UploadFileform(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            file_path = handle_uploaded_file(file)
            
            if file.name.endswith('.csv'):
                data = pd.read_csv(file_path)
            else:
                return render(request, 'csvupload/upload.html', {'form': form, 'error': 'Unsupported file type.'})

            os.remove(file_path)
            
            first_rows = data.head().to_html()
            analysis= data.describe().to_html()
            mean = data.mean().to_frame('Mean').to_html()
            median = data.median().to_frame('Median').to_html()
            std_dev = data.std().to_frame('Standard Deviation').to_html()
            missing_values = data.isnull().sum().to_frame('Missing Values').to_html()

            histograms = []
            for column in data.select_dtypes(include=np.number).columns:
                hist_path = generate_histogram(data[column], column)
                histograms.append(hist_path)

            return render(request, 'csvupload/results.html', {
                'first_rows': first_rows,
                'analysis': analysis,
                'mean': mean,
                'median': median,
                'std_dev': std_dev,
                'missing_values': missing_values,
                'histograms': histograms,
            })
    else:
        form = UploadFileform()
    return render(request, 'csvupload/upload.html', {'form': form})
