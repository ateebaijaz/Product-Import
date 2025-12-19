from django.urls import path
from .views import upload_csv, import_status, upload_page

urlpatterns = [
    path('', upload_page, name='upload_page'),
    path('upload-csv/', upload_csv, name='upload_csv'),
    path('status/<int:job_id>/', import_status, name='import_status'),

]
