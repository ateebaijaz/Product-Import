from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import ImportJob
from .tasks import process_csv_import
from django.views.decorators.csrf import csrf_exempt


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

