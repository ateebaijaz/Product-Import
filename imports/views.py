from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST,require_GET

from .models import ImportJob
from .tasks import process_csv_import
from django.views.decorators.csrf import csrf_exempt

from django.shortcuts import render

def upload_page(request):
    return render(request, "imports/upload.html")

@csrf_exempt
@require_POST
def upload_csv(request):
    file = request.FILES.get('file')

    if not file:
        return JsonResponse(
            {'error': 'No file provided'},
            status=400
        )

    job = ImportJob.objects.create(file=file)

    process_csv_import.delay(job.pk)

    return JsonResponse({
        'job_id': job.pk,
        'status': job.status
    })


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