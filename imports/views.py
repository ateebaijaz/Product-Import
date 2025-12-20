from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST,require_GET

from .models import ImportJob
from .tasks import process_csv_import
from django.views.decorators.csrf import csrf_exempt

from django.shortcuts import render

def upload_page(request):
    return render(request, "imports/upload.html")

import uuid
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from imports.models import ImportJob
from imports.s3 import generate_presigned_upload_url

@require_POST
def get_upload_url(request):
    job = ImportJob.objects.create(status="pending")

    object_key = f"imports/{job.pk}.csv"
    upload_url = generate_presigned_upload_url(object_key)

    job.s3_key = object_key
    job.save(update_fields=["s3_key"])

    return JsonResponse({
        "job_id": job.pk,
        "upload_url": upload_url,
    })




@require_POST
@csrf_exempt
def start_import(request, job_id):
    job = ImportJob.objects.get(pk=job_id)

    process_csv_import.delay(job.pk)

    return JsonResponse({"status": "started"})



@require_GET
def import_status(request, job_id):
    try:
        job = ImportJob.objects.get(pk=job_id)
    except ImportJob.DoesNotExist:
        return JsonResponse(
            {"error": "Job not found"},
            status=404
        )

    return JsonResponse({
        "job_id": job.pk,
        "status": job.status,
        "progress": job.progress,
        "processed_rows": job.processed_rows,
        "total_rows": job.total_rows,
        "message": job.message,
    })