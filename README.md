# LumiCore Data Cleaner - Backend API

Django REST API that fetches messy document data from LumiCore, normalizes it, and submits cleaned data for **100/100 scoring**.

# Lumicore Backend

Lightweight Django backend for Lumicore — core API and cleaning utilities.

**Status:** development

**Contents**
- **Description:** what the project is and its purpose
- **Requirements:** Python, virtualenv, dependencies
- **Quick start:** setup, runserver, migrations
- **Testing:** how to run tests
- **Project structure:** overview of important files and apps
- **Contributing & License**

**Description**

This repository contains the backend for Lumicore built with Django. It provides the core configuration and an app named `cleaning` which implements domain logic, models, and views. The project exposes REST endpoints to normalize and clean incoming document data.

**API Endpoints**

- `POST /api/normalize/` — Normalize raw document payloads into the project's standard schema. Accepts JSON input (single object or array) and returns normalized JSON with deduplication/status information.

**Requirements**
- Python 3.8+ (use a supported venv/virtualenv)
- See [requirements.txt](requirements.txt) for pinned dependencies

**Quick start**
1. Create and activate a virtual environment:

	```bash
	python -m venv .venv
	# Windows
	.\.venv\Scripts\activate 
    or 
    .venv\Scripts\activate.bat 
	# macOS / Linux
	source .venv/bin/activate
	```

2. Install dependencies:

	```bash
    python -m pip install -r requirements.txt
	pip install -r requirements.txt
	```

3. Apply migrations (this project includes `db.sqlite3` for local development):

	```bash
	python manage.py migrate
	```

4. Run the development server:

	```bash
	python manage.py runserver
	```

Visit `http://127.0.0.1:8000/` to view the running app.


**Project structure (overview)**
- [manage.py](manage.py): Django management entrypoint
- [requirements.txt](requirements.txt): Python dependencies
- [db.sqlite3](db.sqlite3): local SQLite database (development)
- [core/](core): project settings, URL configuration, WSGI/ASGI
- [cleaning/](cleaning): Django app for cleaning-related models, views, and utilities


