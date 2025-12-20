from celery import shared_task
import csv

from django.db import transaction

from products.models import Product
from imports.models import ImportJob


@shared_task(bind=True)
def process_csv_import(self, job_id):
    job = ImportJob.objects.get(pk=job_id)

    try:
        job.status = 'processing'
        job.message = 'Reading CSV'
        job.save(update_fields=['status', 'message'])

        # -------- STEP 1: COUNT ROWS (STREAMING, NO MEMORY SPIKE) --------
        with job.file.open(mode='r') as csvfile:
            total_rows = sum(1 for _ in csv.DictReader(csvfile))

        job.total_rows = total_rows
        job.processed_rows = 0
        job.progress = 0
        job.save(update_fields=['total_rows', 'processed_rows', 'progress'])

        # -------- STEP 2: PROCESS CSV IN STREAM --------
        BATCH_SIZE = 50
        batch = {}  # key = sku_lower

        with job.file.open(mode='r') as csvfile:
            reader = csv.DictReader(csvfile)

            for idx, row in enumerate(reader, start=1):
                sku = row.get('sku')
                name = row.get('name')
                description = row.get('description', '')

                if not sku or not name:
                    continue

                normalized_sku = sku.strip()
                sku_lower = normalized_sku.lower()

                batch[sku_lower] = Product(
                    sku=normalized_sku,
                    sku_lower=sku_lower,
                    name=name.strip(),
                    description=description.strip(),
                )

                if len(batch) >= BATCH_SIZE:
                    _bulk_upsert_products(list(batch.values()))
                    batch.clear()

                    job.processed_rows = idx
                    job.progress = round((idx / total_rows) * 100, 2)
                    job.save(update_fields=['processed_rows', 'progress'])

            # -------- STEP 3: FLUSH REMAINING --------
            if batch:
                _bulk_upsert_products(list(batch.values()))
                job.processed_rows = total_rows
                job.progress = 100
                job.save(update_fields=['processed_rows', 'progress'])

        job.status = 'completed'
        job.message = 'Import completed successfully'
        job.save(update_fields=['status', 'message'])

    except Exception as e:
        job.status = 'failed'
        job.message = str(e)
        job.save(update_fields=['status', 'message'])
        raise


def _bulk_upsert_products(products):
    with transaction.atomic():
        Product.objects.bulk_create(
            products,
            update_conflicts=True,
            update_fields=['name', 'description'],
            unique_fields=['sku_lower'],
        )
