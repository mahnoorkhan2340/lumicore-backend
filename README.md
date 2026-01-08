# LumiCore Data Cleaner - Backend API

Django REST API that fetches messy document data from LumiCore, normalizes it, and submits cleaned data for **100/100 scoring**.

## Features

- **Retry logic** for LumiCore API (429/500/503 errors)
- **Field mapping** for 6+ variations per field
- **Date parsing** (DD/MM/YYYY, ISO, compact formats)
- **Deduplication** by `doc_id`
- **CORS** enabled for Next.js frontend
- **Perfect 100/100 scoring** capability

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/fetch/?batch=1` | Fetch raw messy data |
| `POST` | `/api/normalize/` | Normalize raw → standard schema |
| `POST` | `/api/submit/` | Submit cleaned data → get score |

## Quick Start

```bash
# 1. Install dependencies

# 2. Set your candidate ID
set CANDIDATE_ID=candidate-mahnoor-pervaiz-2340

# 3. Run migrations
python manage.py migrate

# 4. Start server
python manage.py runserver
