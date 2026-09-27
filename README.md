# RMG Connect

A small full-stack demo for managing TCS associates who are currently unallocated. React communicates with a Django REST API, and Django stores all application records in SQLite.

## Requirements

- Python 3.10 or newer
- Node.js 18 or newer & npm

## Run the Django backend

From the repository root, create and activate a virtual environment, then install the backend packages:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Django REST Framework, CORS support, and Django are listed in `backend/requirements.txt`. SQLite is configured in `backend/config/settings.py`; no database server or extra package is required.

Create the database tables and demo records:

```powershell
python manage.py makemigrations
python manage.py migrate
python manage.py seed_demo
```

`seed_demo` creates or refreshes the three sample associates and projects and sets demo passwords. It is safe to run again. The initial database file is created at `backend/db.sqlite3` by `migrate`.

Start the API server:

```powershell
python manage.py runserver
```

The API is available at `http://127.0.0.1:8000/api/`.

## Run the React frontend

In another terminal from the repository root:

```powershell
cd frontend
npm install
npm run dev
```

Open the Vite URL printed in the terminal (usually `http://localhost:5173`). Axios is configured in `frontend/src/services/api.js` to call Django with session cookies. Allowed local origins are configured in Django settings.

## Demo login credentials

| Role | Username | Password |
|---|---|---|
| RMG Admin | `admin` | `Admin123!` |
| TCS Associate (Rahul Sharma) | `rahul` | `Associate123!` |
| TCS Associate (Ravi Kumar) | `ravi` | `Associate123!` |
| TCS Associate (Priya Reddy) | `priya` | `Associate123!` |

New associate profiles added by the RMG Admin also get a Django login: the username is the employee ID in lowercase. The initial password is `Welcome123!` unless an optional password is entered in the add form. Change it through Django admin before using this beyond a local demo. To make another administrator, run `python manage.py createsuperuser`. Associate profile details are read-only in the associate UI.

## Demonstrate the workflow

1. Sign in as `admin`. The dashboard counts live associates, open projects, interview calls, and allocated associates.
2. Go to **Projects** and open matching associates for **Python Backend Developer**. Rahul is available, unallocated, meets the 2-year minimum, and matches Python, SQL, and Django (3/3, 100%).
3. Click **Send interview call**, choose date, time, and type, and send it. The API creates an Interview row and sets Rahul's allocation status to `Interviewing`.
4. Sign out and sign in as `rahul`. His dashboard and **My Interview Calls** display the call from the database.
5. Sign back in as `admin`, open **Interview Calls**, set the call to **Selected**, then click **Allocate**. Allocation status changes to `Allocated`; Rahul will no longer appear in available matching results.

## Main API routes

- `POST /api/login/`, `POST /api/logout/`, `GET /api/me/`
- `GET|POST /api/associates/`, `GET|PUT|DELETE /api/associates/<id>/`
- `GET|POST /api/projects/`, `GET|PUT|DELETE /api/projects/<id>/`
- `GET /api/projects/<id>/matches/`
- `GET|POST /api/interviews/`, `GET|PUT|PATCH /api/interviews/<id>/`
- `POST /api/interviews/<id>/allocate/`
- `GET /api/dashboard-summary/`
- `GET /api/my-profile/`, `GET /api/my-opportunities/`, `GET /api/my-interviews/`

The associate and project list APIs accept query filters such as `?allocation_status=Unallocated`, `?name=Rahul`, `?skill=Python`, `?status=Open`, and interview `?status=Scheduled`.

## How it works

The React app handles navigation and forms. Axios sends JSON requests to Django REST Framework through the Vite `/api` development proxy. Django validates data and reads/writes SQLite using Django models. Django session authentication keeps the login simple; Axios includes the CSRF token for write requests. The `Associate.user` one-to-one relationship connects a Django login to its associate profile. An `Interview` has foreign keys to both its `Associate` and `Project`, so one associate or project can have multiple interview records. Projects and associates are otherwise independent.

Skill matching splits comma-separated skills, trims whitespace, compares case-insensitively, and counts each required skill once. A candidate must be available, unallocated, and meet the project's minimum experience. Candidates with at least half of the required skills are returned with the count and percentage. There is no AI or ML.

The interview lifecycle is `Scheduled` → `Selected`, `Rejected`, or `On Hold`. Scheduling changes the associate allocation status to `Interviewing`; a rejected or on-hold result makes the associate `Unallocated` again. A selected associate remains `Interviewing` until the admin allocates them. Allocation checks for a selected interview and updates the associate to `Allocated`, which excludes them from matching.

## Folder structure

```text
backend/   Django settings, REST API, models, migrations, and seed command
frontend/  React pages, reusable components, Axios service, and styling
```
