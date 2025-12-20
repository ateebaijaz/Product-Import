from celery import shared_task
import csv

from django.db import transaction

from products.models import Product
from imports.models import ImportJob
import io
import csv

@shared_task(bind=True)
def process_csv_import(self, job_id):
    job = ImportJob.objects.get(pk=job_id)

    try:
        job.status = "processing"
        job.message = "Processing CSV"
        job.save(update_fields=["status", "message"])

        # ---------- COUNT ROWS ----------
        csv_file = io.StringIO(job.csv_text)
        reader = csv.DictReader(csv_file)
        total_rows = sum(1 for _ in reader)

        job.total_rows = total_rows
        job.processed_rows = 0
        job.progress = 0
        job.save(update_fields=["total_rows", "processed_rows", "progress"])

        # ---------- PROCESS ROWS ----------
        BATCH_SIZE = 50
        batch = {}

        csv_file = io.StringIO(job.csv_text)
        reader = csv.DictReader(csv_file)

        for idx, row in enumerate(reader, start=1):
            sku = row.get("sku")
            name = row.get("name")
            description = row.get("description", "")

            if not sku or not name:
                continue

            sku_clean = sku.strip()
            sku_lower = sku_clean.lower()

            batch[sku_lower] = Product(
                sku=sku_clean,
                sku_lower=sku_lower,
                name=name.strip(),
                description=description.strip(),
            )

            if len(batch) >= BATCH_SIZE:
                _bulk_upsert_products(list(batch.values()))
                batch.clear()

                job.processed_rows = idx
                job.progress = round((idx / total_rows) * 100, 2)
                job.save(update_fields=["processed_rows", "progress"])

        if batch:
            _bulk_upsert_products(list(batch.values()))
            job.processed_rows = total_rows
            job.progress = 100
            job.save(update_fields=["processed_rows", "progress"])

        job.status = "completed"
        job.message = "Import completed successfully"
        job.save(update_fields=["status", "message"])

    except Exception as e:
        job.status = "failed"
        job.message = str(e)
        job.save(update_fields=["status", "message"])
        raise



def _bulk_upsert_products(products):
    with transaction.atomic():
        Product.objects.bulk_create(
            products,
            update_conflicts=True,
            update_fields=['name', 'description'],
            unique_fields=['sku_lower'],
        )
