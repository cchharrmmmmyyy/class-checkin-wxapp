# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A class attendance (班级考勤) system with two parts:
- **WeChat Mini Program** (`miniprogram/`) — student check-in, leave requests, teacher approvals, monitor dashboards
- **Flask Backend** (`backend/`) — REST API with SQLite, serves both the mini program and an admin web panel

## Backend

### Quick start

```bash
cd backend
cp .env.example .env          # edit secrets if needed
pip install -r requirements.txt
python app.py                 # starts on FLASK_HOST:FLASK_PORT (default 0.0.0.0:5000)
```

### Architecture: strict layered design

```
routes/  →  services/  →  dao/  →  SQLite (via utils/db.py)
```

- **`routes/`** — Flask blueprints, parameter validation only, no business logic
- **`services/`** — business logic orchestration
- **`dao/`** — all SQL lives here; `BaseDAO[Generic[T]]` in `base_dao.py` provides typed CRUD with SQL injection guards
- **`models/`** — Python dataclass-like models mapping 1:1 to DB tables
- **`db/schema/`** — numbered SQL migration files (01–17), runnable sequentially to rebuild the full schema
- **`utils/`** — cross-cutting: JWT (`jwt.py`), unified response format (`api_response.py → success()/error()`), custom exceptions (`exceptions.py → ServiceException/AuthenticationException`), geofence distance calculation (`geo.py`), password hashing (`password.py`)

### Key backend details

- **Config**: `config.py` reads `.env`; all required keys fail-fast on startup with `ValueError`
- **Auth**: JWT-based; `utils/jwt.py` has `generate_token()` / `decode_token()` / `require_auth` decorator
- **API response envelope**: every response is `{code, message, data}` — `success(data)` and `error(message, code, http_status)` from `utils/api_response.py`
- **Error codes**: defined in `utils/error_codes.py`
- **Admin panel**: served by Flask at `/admin` — Vue 3 + Element Plus SPA, served from `templates/` and `static/`
- **Test data**: set `INSERT_TEST_DATA=True` in `.env` to seed demo data on startup
- **DB init**: `check_and_init_database()` runs at module import time (not just `__main__`), so WSGI deployments also initialize

### Route to file mapping (for tracing a feature)

| Feature | Route | Service | DAO |
|---|---|---|---|
| Login | `routes/auth.py` | `services/auth_service.py` | `dao/user_dao.py` |
| Student punch | `routes/student.py` | `services/punch_service.py` | `dao/punch_dao.py`, `dao/punch_geofence_dao.py` |
| Leave request | `routes/student.py` | `services/leave_service.py` | `dao/leave_dao.py` |
| Makeup request | `routes/student.py` | `services/makeup_service.py` | `dao/makeup_request_dao.py` |
| Teacher approval | `routes/teacher.py` | `services/leave_service.py` / `makeup_service.py` | `dao/leave_dao.py`, `dao/makeup_request_dao.py` |
| Monitor dashboard | `routes/student.py` (monitor endpoints) | `services/monitor_service.py` | `dao/punch_dao.py`, `dao/leave_dao.py` |
| Admin CRUD | `routes/admin/` | `services/admin_*_service.py` | `dao/*_dao.py` |
| Notifications | `routes/common.py` | `services/notification_service.py` | `dao/notification_dao.py` |

## Mini Program (Frontend)

### Key files

- **`app.js`** — global state (userInfo, token in `wx.StorageSync`), role-based navigation via `navigateByRole()`
- **`network/request.js`** — HTTP client wrapping `wx.request`; expects unified `{code, message, data}` envelope; automatically attaches `Authorization: Bearer` header from storage; GET/DELETE params go in query string
- **`network/api.js`** — typed API layer; every backend endpoint is wrapped here, pages import this or call `request()` directly
- **`config/api.js`** — `baseUrl`, `timeout`, and `API_ENDPOINTS` map; change `env` to switch dev/prod

### Role-based page routing

- **Student/Monitor**: lands on `pages/student/index/index` (punch page)
- **Teacher**: lands on `pages/teacher/classes/classes` (class list)
- **Admin**: told to use the browser admin panel
- After login, `app.navigateByRole(role)` uses `wx.reLaunch` to redirect

### Component patterns

- **`components/custom-tabbar/`** — app-global tab bar (registered in `app.json` `usingComponents`)
- **`components/student-tabbar/`** and **`components/teacher-tabbar/`** — page-level tab bars (some pages use these instead)
- **`components/navbar/`** — custom navigation bar

### Styling

- CSS custom properties defined in `styles/theme.wxss` — use these variables, not hardcoded colors
- Theme switching via `utils/theme.js` (`ThemeManager` class); themes: default, blue, purple, red, dark
- Utility classes in `styles/base.wxss` (flex, spacing, typography)

### Known issues / code debt

- The frontend used to call `request()` directly in pages; the `network/api.js` wrapper now exists and is consistently used. All active pages (app.json) import from `api.js`.

## Role system

4 roles with different permissions:
- **student** — punch in, apply for leave/makeup, view personal records
- **monitor** (班委) — same pages as student + monitor dashboard showing class punch status, pending requests
- **teacher** — view classes, approve/reject leave and makeup, manage monitors
- **admin** — full CRUD on org structure, users, punch rules; dashboard with stats/trends/export; web-only
