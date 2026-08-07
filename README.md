# TaskFlow — Team Task Manager

A full-stack team task management web app with **role-based access control** (Admin/Member), project & team management, task assignment, status tracking, and a live dashboard.

**Stack:** Django 5.2 + Django REST Framework (JWT) · React 18 + Vite · PostgreSQL (Railway) / SQLite (local)

---

## ✨ Features

- **Authentication** — signup, login, JWT (access + refresh), auto token refresh
- **Projects & teams** — create projects, invite members, assign per-project roles (Admin/Member)
- **Tasks** — create, assign, set status/priority/due date, comments
- **Dashboard** — total tasks, status breakdown, overdue, my tasks, project count
- **Role-based access control**
  - **Project Admin**: create/edit/delete project, manage team, create/edit/delete tasks, assign tasks
  - **Project Member**: view project & tasks, update status/priority of their own assigned tasks, comment
  - **Platform Admin**: platform-wide access (account-level `role=admin`)
- **Validations & relationships** — custom user model, project↔membership↔task↔comment relations, assignee must be a project member, due date not in the past, duplicate-email rejection

---

## 🚀 Live demo

**Live URL:** `https://YOUR-APP.up.railway.app` *(set after deploying — see below)*

| Demo account | Password      | Role |
|--------------|---------------|------|
| admin@example.com | `admin12345` | Platform Admin |
| alice@example.com | `password123` | Member (project admin) |
| bob@example.com   | `password123` | Member |
| carol@example.com | `password123` | Member |

> Run `python manage.py seed_demo` to create these demo users, projects and tasks.

---

## 🧱 Project structure

```
├── backend/                  # Django REST API
│   ├── accounts/             # custom User, register/login/me, user search
│   ├── projects/             # Project, Membership, RBAC permissions
│   ├── tasks/                # Task, Comment, dashboard
│   ├── config/               # settings, root urls
│   ├── tests.py              # API + RBAC test suite (12 tests)
│   └── requirements.txt
├── frontend/                 # React + Vite SPA
│   ├── src/api/              # axios client (JWT + refresh interceptor)
│   ├── src/context/          # auth context
│   ├── src/pages/            # Login, Register, Dashboard, Projects, ProjectDetail, Tasks
│   └── server.js             # Node static server + /api proxy
└── railway.json              # Railway multi-service config
```

---

## 📦 Running locally

### 1. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo       # optional demo data
python manage.py runserver
```

API runs at `http://localhost:8000` (health check: `GET /api/health/`).

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

App runs at `http://localhost:5173`. The Vite dev server proxies `/api` to `localhost:8000`.

### Run tests

```bash
cd backend
python manage.py test
```

---

## 🔌 REST API overview

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/auth/register/` | public | Create account, returns tokens |
| POST | `/api/auth/login/` | public | Login, returns tokens |
| POST | `/api/auth/token/refresh/` | refresh | Refresh access token |
| GET | `/api/auth/me/` | JWT | Current user |
| GET | `/api/auth/users/?q=` | JWT | Search users (for adding team members) |
| GET/POST | `/api/projects/` | JWT | List / create projects |
| GET/PATCH/DELETE | `/api/projects/:id/` | JWT | Project detail / update / delete (admin) |
| GET/POST | `/api/projects/:id/members/` | admin | List / add members |
| PATCH/DELETE | `/api/projects/:id/members/:mid/` | admin | Change role / remove member |
| GET/POST | `/api/tasks/?project=` | JWT | List / create tasks (admin creates) |
| GET/PATCH/DELETE | `/api/tasks/:id/` | JWT | Task detail / update (admin or assignee) / delete (admin) |
| GET/POST | `/api/tasks/:id/comments/` | JWT | List / add comments |
| GET | `/api/tasks/dashboard/` | JWT | Dashboard statistics |

---

## 🌐 Deployment (Railway)

The repo ships with a `railway.json` that defines two services.

### One-time setup

1. **Push this project to GitHub**, then go to [railway.app](https://railway.app) → **New Project** → **Deploy from GitHub repo** → pick the repo.
2. Railway reads `railway.json` and creates two services: **backend** and **frontend**.

### Backend service variables

| Variable | Value |
|----------|-------|
| `DJANGO_SECRET_KEY` | a long random string (e.g. from `python -c "import secrets; print(secrets.token_urlsafe(50))"`) |
| `DJANGO_DEBUG` | `False` |
| `DJANGO_ALLOWED_HOSTS` | `backend-production-xxxx.up.railway.app` (your backend domain) |
| `DATABASE_URL` | auto-provided by Railway Postgres |

Add a **PostgreSQL** database via the Railway dashboard — Railway injects `DATABASE_URL` automatically.

> On first deploy, `python manage.py migrate` runs automatically via the start command.

### Frontend service variable

| Variable | Value |
|----------|-------|
| `API_URL` | `https://backend-production-xxxx.up.railway.app` (the backend's public URL) |

### Wire them together

1. Backend service → **Settings** → copy the **Public Networking / Production Domain**.
2. Set it as `API_URL` on the **frontend** service and redeploy.
3. Open the frontend's generated domain → the app is live. The Node server serves the built React app and proxies `/api` to the backend, so no CORS config is needed in production.

### Optional: seed demo data

```bash
# From the backend service → Deployments → open a shell, or run:
python manage.py seed_demo
```

---

## 🧪 Notes

- Frontend stores JWT in `localStorage`; the axios interceptor transparently refreshes expired access tokens using the refresh token.
- Production static files are served by WhiteNoise (`collectstatic` runs on deploy).
- CORS is only relevant for local dev (frontend proxies in production).

## 📄 License

MIT
