# LumiCore Data Cleaner - Backend API

Django REST API that fetches messy document data from LumiCore, normalizes it, and submits cleaned data for **100/100 scoring**.

## Features

- **Normalization**
- **Field mapping** for 6+ variations per field
- **Date parsing** (DD/MM/YYYY, ISO, compact formats)
- **Deduplication** by `doc_id`
- **CORS** enabled for Next.js frontend
- **Perfect 100/100 scoring** capability

## API Endpoints

| `POST` | `/api/normalize/` | Normalize raw → standard schema |


## Quick Start

```bash
# 1. Install dependencies 

# 2. Set your candidate ID
set CANDIDATE_ID=candidate-mahnoor-pervaiz-2340

# 3. Run migrations
python manage.py migrate

# 4. Start server
python manage.py runserver
