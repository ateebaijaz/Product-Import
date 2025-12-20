from django.urls import path
from .views import import_status, upload_page, get_upload_url, start_import

urlpatterns = [
    path('', upload_page, name='upload_page'),
    path("get-upload-url/", get_upload_url),
    path("start-import/<int:job_id>/", start_import),

    # path('upload-csv/', upload_csv, name='upload_csv'),
    path('status/<int:job_id>/', import_status, name='import_status'),

]
