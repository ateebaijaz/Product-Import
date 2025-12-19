from celery import shared_task
import time

from imports.models import ImportJob

@shared_task(bind=True)
def process_csv_import(self, job_id):
    job = ImportJob.objects.get(id=job_id)

    # placeholder – real logic comes later
    job.status = 'processing'
    job.message = 'Import started'
    job.save()
