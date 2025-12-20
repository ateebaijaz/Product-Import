from celery import shared_task
import csv
import os
import boto3

from django.db import transaction

from products.models import Product
from imports.models import ImportJob


@shared_task(bind=True)
def process_csv_import(self, job_id):
    job = ImportJob.objects.get(pk=job_id)

    try:
        # ------------------ INIT ------------------
        job.status = "processing"
        job.message = "Processing CSV"
        job.save(update_fields=["status", "message"])

        s3 = boto3.client(
            "s3",
            region_name=os.getenv("AWS_REGION"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        )

        bucket = os.getenv("AWS_S3_BUCKET_NAME")

        obj = s3.get_object(
            Bucket=bucket,
            Key=job.s3_key,
        )

        # ------------------ STREAM CSV ------------------
        # Decode lines lazily (no full file load)
        lines = (line.decode("utf-8") for line in obj["Body"].iter_lines())
        reader = csv.DictReader(lines)

        # ------------------ COUNT ROWS ------------------
        # We must count rows once to calculate progress
        rows = list(reader)
        total_rows = len(rows)

        job.total_rows = total_rows
        job.processed_rows = 0
        job.progress = 0
        job.save(update_fields=["total_rows", "processed_rows", "progress"])

        # ------------------ PROCESS ROWS ------------------
        BATCH_SIZE = 50
        batch = {}

        for idx, row in enumerate(rows, start=1):
            sku = row.get("sku")
            name = row.get("name")
            description = row.get("description", "")

            if not sku or not name:
                continue

            sku_clean = sku.strip()
            sku_lower = sku_clean.lower()

            # Deduplicate within batch (last row wins)
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

        # ------------------ FLUSH REMAINING ------------------
        if batch:
            _bulk_upsert_products(list(batch.values()))

        job.processed_rows = total_rows
        job.progress = 100
        job.status = "completed"
        job.message = "Import completed successfully"
        job.save(update_fields=[
            "processed_rows",
            "progress",
            "status",
            "message",
        ])

    except Exception as e:
        job.status = "failed"
        job.message = str(e)
        job.save(update_fields=["status", "message"])
        raise


def _bulk_upsert_products(products):
    """
    Conflict-safe bulk upsert using sku_lower uniqueness.
    Guarantees:
    - No duplicates
    - Last write wins
    - Atomic per batch
    """
    with transaction.atomic():
        Product.objects.bulk_create(
            products,
            update_conflicts=True,
            update_fields=["name", "description"],
            unique_fields=["sku_lower"],
        )
