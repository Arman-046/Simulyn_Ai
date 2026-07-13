# Developer Guide

## Local Environment Setup
1. Clone the repository.
2. Create a virtual environment: `python -m venv venv`
3. Activate it: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Linux/Mac)
4. Install dependencies: `pip install -r requirements.txt`

## Running Local Infrastructure
```bash
docker-compose up -d
```
This provisions PostgreSQL on `localhost:5432` and Redis on `localhost:6379`.

## Database Migrations
Always run Alembic from the root directory but explicitly pass the config file path:
```bash
alembic -c backend/alembic.ini upgrade head
```
To generate a new migration:
```bash
alembic -c backend/alembic.ini revision --autogenerate -m "description"
```

## Running the Application
**Backend:**
```bash
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```
**Frontend:**
```bash
python server.py 3000
```

## Testing Workflow
We utilize `pytest` for backend verification.
```bash
export PYTHONPATH="."
pytest backend/tests/
```
*Note for Windows users:* Use `$env:PYTHONPATH="."` in PowerShell.

## Common Issues
- **`UndefinedColumnError: column "payload" does not exist`**: You are attempting to query the legacy schema. We migrated to `population_data` in PKG-004. Please run `alembic upgrade head`.
- **`No 'script_location' key found in configuration`**: You ran `alembic` without the `-c backend/alembic.ini` flag.
