<div align="center">

# KaamSathi — Team Task Manager

A full-stack team task management application with role-based access control.

**[Live Demo](https://frontend-production-7a0f.up.railway.app) · [Backend API](https://backend-production-c4f6.up.railway.app) · [Project on GitHub](https://github.com/anishraja04/team-task-manager)**

**Django REST Framework · React · PostgreSQL · JWT Auth · Deployed on Railway**

</div>

---

## Overview

KaamSathi (Hindi: काम साथी, "work partner") helps teams organize work into **projects**, assign **tasks**, and track progress through a live dashboard. Access is controlled by **role-based permissions** (Admin / Member) at both the platform and project level, ensuring that only authorized users can create, edit, or assign work. The demo data is seeded with Indian team members and real-world style projects like **Hindi LLM Model Training** and **UPI Fraud Detection ML Model**.

The application is a classic three-tier architecture:

- **Backend** — a REST API built with Django 5.2 and Django REST Framework, secured with JWT (SimpleJWT), connected to PostgreSQL.
- **Frontend** — a single-page application built with React 18 and Vite, with route-level auth guards and an axios client that transparently refreshes expired tokens.
- **Infrastructure** — two services deployed on Railway; the frontend proxies `/api` to the backend, so there is no CORS configuration needed in production.

---

## Features

### Authentication
- Email + password signup and login
- JWT access + refresh tokens with automatic silent refresh
- Password hashing and validation out of the box

### Projects & Teams
- Create, edit, and delete projects
- Invite users to a project as a **Member** or **Admin**
- Change member roles or remove members; the project owner cannot be removed

### Tasks
- Create tasks with title, description, status, priority, and due date
- Assign tasks to project members only
- Update status and priority (assignees on their own tasks; admins on any task)
- Add comments and track task history

### Dashboard
- Live counts: total, by status, completed, overdue
- Personal view: "my tasks" and "my overdue"
- Recent tasks table

### Role-Based Access Control (RBAC)

| Role | Capabilities |
|------|--------------|
| **Platform Admin** | Access to every project, team, and task across the platform |
| **Project Admin** | Manage the project, team members, and all tasks; assign work |
| **Project Member** | View the project and its tasks; update status/priority of their own assigned tasks; comment |

### Validation & Data Integrity
- Custom `User` model (email is the unique identifier)
- Relations: `Project` ↔ `Membership` ↔ `Task` ↔ `Comment`
- Assignees must be project members
- Due dates cannot be in the past on creation
- Duplicate emails rejected at registration

---

## Demo

Sign in with any of the accounts below (seeded automatically on deploy):

| Email | Password | Role |
|-------|----------|------|
| `admin@example.com` | `admin12345` | Platform Admin |
| `rohan@example.com` | `password123` | Project Admin |
| `priya@example.com` | `password123` | Member |
| `arjun@example.com` | `password123` | Member |
| `ananya@example.com` | `password123` | Member |

You can also register a new account from the sign-up page.

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.13 · Django 5.2 · Django REST Framework · SimpleJWT |
| Database | PostgreSQL (Railway) · SQLite (local dev) |
| Frontend | React 18 · Vite 5 · React Router · Axios |
| Deployment | Railway (Nixpacks) · Gunicorn · WhiteNoise · Node static server + reverse proxy |

---

## Project Structure

```
.
├── backend/                     # Django REST API
│   ├── accounts/                # User model, register/login/me, user search
│   ├── projects/                # Project, Membership, RBAC permissions
│   ├── tasks/                   # Task, Comment, dashboard endpoint
│   ├── config/                  # Django settings and URL routing
│   ├── tests.py                 # 12 automated API + RBAC tests
│   ├── requirements.txt
│   └── railway.json             # Railway service configuration
├── frontend/                    # React SPA
│   ├── src/api/                 # Axios client + JWT refresh interceptor
│   ├── src/context/             # Authentication context
│   ├── src/components/          # Reusable UI (modals, layout)
│   ├── src/pages/               # Login, Register, Dashboard, Projects, Tasks
│   ├── server.js                # Production static server + /api proxy
│   └── railway.json             # Railway service configuration
└── railway.json                 # Root multi-service Railway config
```

---

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+

### 1. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo       # optional: demo users, projects, tasks
python manage.py runserver
```

The API is available at `http://localhost:8000` — verify with `GET /api/health/`.

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

The app runs at `http://localhost:5173`. The Vite dev server proxies `/api` requests to `localhost:8000`, so no CORS setup is required.

### 3. Tests

```bash
cd backend
python manage.py test
```

The suite covers authentication, RBAC enforcement, task assignment rules, member management, and dashboard aggregation.

---

## API Reference

Base URL: `https://backend-production-c4f6.up.railway.app` (locally `http://localhost:8000`)

All endpoints except the public auth routes require the header `Authorization: Bearer <access_token>`.

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| `POST` | `/api/auth/register/` | Public | Create an account, returns tokens |
| `POST` | `/api/auth/login/` | Public | Authenticate, returns tokens |
| `POST` | `/api/auth/token/refresh/` | Refresh token | Issue a new access token |
| `GET` | `/api/auth/me/` | Authenticated | Current user profile |
| `GET` | `/api/auth/users/?q=` | Authenticated | Search users by email/name/username |
| `GET` `POST` | `/api/projects/` | Authenticated | List / create projects |
| `GET` `PATCH` `DELETE` | `/api/projects/:id/` | Member / Admin | Retrieve, update, delete a project |
| `GET` `POST` | `/api/projects/:id/members/` | Admin | List / add team members |
| `PATCH` `DELETE` | `/api/projects/:id/members/:mid/` | Admin | Change role / remove member |
| `GET` `POST` | `/api/tasks/?project=` | Authenticated | List / create tasks |
| `GET` `PATCH` `DELETE` | `/api/tasks/:id/` | Member / Admin | Retrieve, update, delete a task |
| `GET` `POST` | `/api/tasks/:id/comments/` | Member | List / add task comments |
| `GET` | `/api/tasks/dashboard/` | Authenticated | Dashboard statistics |

### Example — Log in

```bash
curl -X POST https://backend-production-c4f6.up.railway.app/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "bob@example.com", "password": "password123"}'
```

### Example — Create a task (admin only)

```bash
curl -X POST https://backend-production-c4f6.up.railway.app/api/tasks/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"title": "Write API docs", "project": 1, "assignee": 3, "priority": "high"}'
```

---

## Deployment (Railway)

The repository includes a multi-service `railway.json` that provisions two services: `backend` and `frontend`.

### Services

| Service | Build | Start command |
|---------|-------|---------------|
| `backend` | Nixpacks (Python) | Migrate → collect static → seed demo → Gunicorn |
| `frontend` | Nixpacks (Node) | `npm run build` → serve `dist` + proxy `/api` |

### Backend environment variables

| Variable | Description |
|----------|-------------|
| `DJANGO_SECRET_KEY` | Generate with `python -c "import secrets; print(secrets.token_urlsafe(50))"` |
| `DJANGO_DEBUG` | `False` in production |
| `DJANGO_ALLOWED_HOSTS` | Your backend domain (e.g. `backend-production-xxxx.up.railway.app`) |
| `DATABASE_URL` | Provided automatically by the Railway Postgres plugin |

### Frontend environment variables

| Variable | Description |
|----------|-------------|
| `API_URL` | Public URL of the backend service |

Migrations and demo data seeding run automatically on every deploy, so the database is always ready.

---

## Roadmap

- Email notifications for task assignment and due dates
- File attachments on tasks
- Task filtering by assignee, priority, and due date on the dashboard
- OAuth sign-in (Google / GitHub)
- Dark mode

---

## License

Distributed under the MIT License.
