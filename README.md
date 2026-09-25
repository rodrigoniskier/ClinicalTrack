# ClinicalTrack

> **Portfolio edition:** a clean, generic training-placement management platform with no institutional data or inherited repository history.

ClinicalTrack is designed for internships, clinical placements, residencies, apprenticeships and other supervised practical-learning programs.

## Portfolio snapshot

This project demonstrates domain modeling, role-based workflows, object-level authorization, relational data, evaluations, migrations, tests and production-oriented Django configuration.

**Stack:** Django · PostgreSQL/SQLite · RBAC · Migrations · Tests · Gunicorn · WhiteNoise

## Roles

- **Administrator** — manages users, sites, areas, periods, placements and notices through Django Admin.
- **Supervisor** — sees only assigned placements and records evaluations for those trainees.
- **Trainee** — sees own placements and only evaluations explicitly shared with them.

## Core model

`TrainingArea → RotationPeriod → Placement ← TrainingSite`

Each placement binds one trainee to one supervisor, site and period. Evaluation authorization is checked against that assignment on the server; changing a URL or form value cannot grant access to another supervisor's trainee.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

Synthetic demo credentials created by `seed_demo`:

- `admin` / `Demo-Admin-12345`
- `supervisor.demo` / `Demo-Supervisor-12345`
- `trainee.demo` / `Demo-Trainee-12345`

These are demo-only accounts and must never be used in production.

## Production

Set `DATABASE_URL` to PostgreSQL, provide a stable `SECRET_KEY`, set `DEBUG=0`, configure `ALLOWED_HOSTS` / `CSRF_TRUSTED_ORIGINS`, and run:

```bash
python manage.py check --deploy
python manage.py migrate
python manage.py collectstatic --noinput
gunicorn clinicaltrack.wsgi:application
```

## Origin and privacy

The private operational system that inspired this case remains separate. ClinicalTrack uses generic terminology (`trainee`, `supervisor`, `training site`, `placement`) and synthetic data, and begins with a new public Git history rather than exposing the history of the original deployment.
