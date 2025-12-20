# Product Import System (Django + PostgreSQL + Celery)

This project implements an **async CSV product import system** with real time progress percentage tracking, enables to handle **large CSV files (50k+ rows)** 

The system is built using **Django**, **PostgreSQL**, **Celery**, and **Redis**, with a simple UI for usability

---

## ✨ Features

### 1. Asynchronous CSV Import
- Upload large CSV files without HTTP timeouts
- Background processing using Celery
- Chunks/batches database inserts for performance (bulk insertion)
- Case insensitive SKU handling
- Duplicate SKUs are overwritten 

### 2. Real-Time Progress Tracking
- Import progress tracked via `ImportJob`
- UI polls backend for live status updates
- Displays processed rows, total rows, percentage, and messages

### 3. Product Management UI
- List products with pagination
- Filter products by:
  - SKU (searchable)
  - Active / Inactive status
- Toggle product `is_active` state
- Bulk delete all products

### 4. Simple Architecture
- **ImportJob** is the single source of truth for import status
- **Product** table enforces data integrity at DB level

---

## 🧠 Architecture Overview

### Import Flow

1. User uploads CSV via UI
2. Django saves file and creates an `ImportJob`
3. Celery worker processes CSV asynchronously
4. Products are inserted/updated in chunks
5. ImportJob is updated with progress and status
6. Polling on status endpointsa to show progress


---

## 🗃️ Data Model

### Product
- `sku` (unique, case-insensitive)
- `name`
- `description`
- `is_active`

### ImportJob
- Stores uploaded file
- Tracks status (`pending`, `processing`, `completed`, `failed`)
- Tracks progress (`processed_rows`, `total_rows`, `progress`)
- Durable and crash-safe

---

## ⚙️ Tech Stack

- **Backend**: Django
- **Database**: PostgreSQL
- **Async Tasks**: Celery
- **Message Broker**: Redis
- **Frontend**: Django Templates + Vanilla JS

---

## 🚀 Running Locally

### 1. Clone repository
```bash
git clone <repo-url>
cd product-import


python -m venv venv
source venv/bin/activate


pip install -r requirements.txt


DATABASE_URL=postgresql://user:password@localhost:5432/dbname
REDIS_URL=redis://localhost:6379/0


python manage.py migrate


redis-server
celery -A config worker -l info
python manage.py runserver

CSV shoud contain headers
sku,name,description

SKU1,Product 1,Sample description
SKU2,Product 2,Another description
