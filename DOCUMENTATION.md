# Workflow Test App — Documentation

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Data Model](#data-model)
- [Features](#features)
  - [Authentication](#authentication)
  - [Task List (Home Page)](#task-list-home-page)
  - [Task Summary Bar](#task-summary-bar)
  - [Create Task](#create-task)
  - [Task Detail Page](#task-detail-page)
  - [Task Description](#task-description)
  - [Edit Task](#edit-task)
  - [Change Task Status](#change-task-status)
  - [Delete Task](#delete-task)
  - [Subtasks](#subtasks)
  - [Timestamps](#timestamps)
  - [Persistent Storage](#persistent-storage)
- [REST API Reference](#rest-api-reference)
  - [Authentication Endpoints](#authentication-endpoints)
  - [Task Endpoints](#task-endpoints)
  - [Subtask Endpoints](#subtask-endpoints)
- [Pages & Routes](#pages--routes)
- [Project Structure](#project-structure)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Testing](#testing)
  - [Unit Tests](#unit-tests)
  - [UI Tests (Selenium)](#ui-tests-selenium)
  - [Running Tests](#running-tests)
  - [Test Coverage by Feature](#test-coverage-by-feature)
  - [Test Architecture](#test-architecture)
- [CI/CD](#cicd)

---

## Overview

Workflow Test App is a task tracker web application built with Flask. Users create an account, log in, and manage their personal tasks through a clean web interface and REST API. Each task supports a title, description, status tracking, subtasks, and automatic timestamps. Data is stored in SQLite and persists across server restarts.

## Architecture

```
Browser ──► Flask (app.py) ──► SQLite (tasks.db)
  │              │
  │              ├── /signup, /login, /logout  → Authentication
  │              ├── GET /                     → renders index.html (user's tasks)
  │              ├── GET /task/<id>            → renders detail.html (task detail)
  │              ├── /api/tasks/*              → JSON REST API (tasks)
  │              └── /api/tasks/*/subtasks/*   → JSON REST API (subtasks)
  │
  ├── static/style.css  (styling)
  └── vanilla JavaScript (async fetch for API calls)
```

- **Server-side rendering**: Pages are rendered using Jinja2 templates with initial data from the server.
- **Client-side updates**: After the initial load, JavaScript uses `fetch()` to call the REST API and updates the DOM without full page reloads.
- **SQLite storage**: Tasks, subtasks, and users are stored in a SQLite database (`tasks.db`). Data persists across server restarts.
- **Session-based auth**: Flask sessions with signed cookies. Passwords are hashed using werkzeug's `generate_password_hash` (pbkdf2).
- **Per-user isolation**: All task queries are filtered by the logged-in user's ID. Users cannot see or modify other users' tasks.

## Data Model

### User

| Field           | Type   | Description                                |
|-----------------|--------|--------------------------------------------|
| `id`            | int    | Auto-incremented primary key               |
| `username`      | string | Unique username (required)                 |
| `password_hash` | string | Hashed password (werkzeug pbkdf2)          |
| `created_at`    | string | ISO 8601 UTC timestamp                     |

### Task

| Field         | Type   | Description                                      |
|---------------|--------|--------------------------------------------------|
| `id`          | int    | Auto-incremented primary key                     |
| `user_id`     | int    | Foreign key to users table (owner)               |
| `title`       | string | The task title (required)                        |
| `description` | string | Optional text description (default: `""`)        |
| `status`      | string | Either `"pending"` or `"done"` (default: `"pending"`) |
| `created_at`  | string | ISO 8601 UTC timestamp, set at creation          |
| `modified_at` | string | ISO 8601 UTC timestamp, updated on every change  |
| `subtasks`    | array  | List of subtask objects (from subtasks table)    |

**Example task object (API response):**

```json
{
  "id": 1,
  "title": "Review pull request",
  "description": "Check the auth module changes",
  "status": "pending",
  "created_at": "2026-11-27T09:14:58.435252+00:00",
  "modified_at": "2026-11-27T09:14:58.435252+00:00",
  "subtasks": [
    { "id": 1, "title": "Review code", "status": "done" },
    { "id": 2, "title": "Run tests", "status": "pending" }
  ]
}
```

### Subtask

| Field    | Type   | Description                                      |
|----------|--------|--------------------------------------------------|
| `id`     | int    | Auto-incremented primary key                     |
| `task_id`| int    | Foreign key to tasks table (cascade on delete)   |
| `title`  | string | The subtask title (required)                     |
| `status` | string | Either `"pending"` or `"done"` (default: `"pending"`) |

### Database Schema

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT DEFAULT '',
    status TEXT DEFAULT 'pending',
    created_at TEXT NOT NULL,
    modified_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE subtasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
);
```

---

## Features

### Authentication

The app requires users to create an account and log in before accessing tasks.

**Signup** (`/signup`):
- Form with username, password, and confirm password fields
- Validation: username required, password minimum 4 characters, passwords must match
- Duplicate usernames are rejected with an error message
- On success, redirects to the login page

**Login** (`/login`):
- Form with username and password fields
- Validates credentials against the database (hashed password comparison)
- On success, creates a session and redirects to the home page
- Invalid credentials show an error message

**Logout** (`/logout`):
- Clears the session and redirects to the login page

**Session management:**
- Session cookie is signed with a secret key
- All task routes check for a valid session via `login_required` decorator
- Unauthenticated requests to protected routes redirect to `/login`

**Nav bar:**
- Displayed on the home page and detail page
- Shows the logged-in username and a "Logout" link

### Task List (Home Page)

**URL:** `/` (requires login)

The home page displays the logged-in user's tasks in a card-based list. Each task card shows:

- **Status badge** — Color-coded label (`pending` in amber, `done` in green)
- **Title** — Clickable link that navigates to the task's detail page
- **Description preview** — First 80 characters of the description (if present)
- **Subtask count** — "X/Y subtasks done" indicator (if subtasks exist)
- **Created date** — When the task was created (formatted in the user's locale)
- **Modified date** — When the task was last updated
- **Toggle button** — Switches the task status between pending and done
- **Delete button** — Removes the task from the list

The list updates dynamically without a full page reload after any action.

### Task Summary Bar

Displayed above the task list when at least one task exists. Shows:

- **Total** — Total number of tasks
- **Pending** — Count of tasks with status `"pending"` (amber)
- **Done** — Count of tasks with status `"done"` (green)

The summary bar updates automatically whenever tasks are added, modified, or deleted.

### Create Task

A form at the top of the home page with a text input and "Add" button. Enter a title and submit to create a new task. The task is created with:

- Owner: the logged-in user
- Description: empty
- Status: `pending`
- Subtasks: empty list
- Timestamps: `created_at` and `modified_at` set to the current UTC time

The task list and summary bar update immediately after creation.

### Task Detail Page

**URL:** `/task/<id>` (requires login, must be the task owner)

A dedicated page for viewing and managing a single task. Accessed by clicking a task's title on the home page. The detail page includes:

- **Nav bar** — Username and logout link
- **Back link** — Returns to the task list
- **Status badge** — Shows current status with color coding
- **Task heading** — Displays the task ID (e.g., "Task #1")
- **Title input** — Editable text field pre-filled with the current title
- **Description textarea** — Editable multi-line text area for the task description
- **Status dropdown** — Select between "Pending" and "Done"
- **Timestamps** — Created and modified dates displayed below the form
- **Save Changes button** — Saves edits to title, description, and status
- **Delete Task button** — Deletes the task after confirmation
- **Subtasks section** — Add, toggle, and delete subtasks (see below)

After saving, a green success message appears and the page updates in-place (no reload). After deleting, the user is redirected to the home page.

### Task Description

Each task has an optional text description field:

- Editable via a textarea on the detail page
- Saved along with title and status when clicking "Save Changes"
- Shown as a truncated preview (first 80 characters) on the home page task cards
- Defaults to an empty string when not provided

### Edit Task

Tasks can be edited in two ways:

1. **From the detail page** — Change the title, description, or status and click "Save Changes". All fields are sent to the API in a single PATCH request.
2. **Via the API** — Send a PATCH request with any combination of `title`, `description`, and/or `status` fields.

Every edit updates the `modified_at` timestamp automatically.

### Change Task Status

Task status can be toggled in two ways:

1. **From the home page** — Click the "Toggle" button on a task card to switch between `pending` and `done`.
2. **From the detail page** — Select the desired status from the dropdown and click "Save Changes".

### Delete Task

Tasks can be deleted in two ways:

1. **From the home page** — Click the "Delete" button on a task card. The task is removed immediately.
2. **From the detail page** — Click the "Delete Task" button. A confirmation dialog appears ("Are you sure you want to delete this task?"). On confirmation, the task is deleted and the user is redirected to the home page.

Deleting a task also deletes all its subtasks (cascade delete).

### Subtasks

Each task can have zero or more subtasks, each with its own status. Subtasks are managed from the task detail page.

**Adding a subtask:**
- A form below the "Subtasks" heading with a text input and "Add" button
- Enter a subtask title and click Add — it appears in the list immediately

**Toggling subtask status:**
- Each subtask row has a "Toggle" button to switch between `pending` and `done`
- Done subtasks display with strikethrough text styling

**Deleting a subtask:**
- Each subtask row has a "Delete" button to remove it

**Subtask indicators on home page:**
- When a task has subtasks, a "X/Y subtasks done" count appears on its card

**All subtask operations** (create, toggle, delete) automatically update the parent task's `modified_at` timestamp.

When no subtasks exist, a "No subtasks yet." placeholder is displayed.

### Timestamps

Every task records two timestamps in ISO 8601 UTC format:

- **Created date** — Set once when the task is created. Never changes.
- **Modified date** — Initially the same as the created date. Updated to the current UTC time on every PATCH request (title, description, or status change) and on every subtask operation.

Timestamps are displayed in the user's local timezone and format using `toLocaleString()`.

### Persistent Storage

The app uses SQLite for data persistence:

- **Database file:** `tasks.db` (auto-created on first run)
- **Tables:** `users`, `tasks`, `subtasks`
- **Foreign keys:** Tasks reference users; subtasks reference tasks with cascade delete
- **Data survives** server restarts — no data loss between sessions
- **Test isolation:** Unit tests use temporary SQLite files that are cleaned up after each test

---

## REST API Reference

Base URL: `http://localhost:5000`

All task and subtask endpoints require an authenticated session. API endpoints return JSON. Request bodies must be sent as `Content-Type: application/json`.

### Authentication Endpoints

#### Signup

```
GET  /signup          — Render signup form
POST /signup          — Create account (form data: username, password, confirm)
```

Redirects to `/login` on success. Returns the form with an error message on validation failure.

#### Login

```
GET  /login           — Render login form
POST /login           — Authenticate (form data: username, password)
```

Sets a session cookie and redirects to `/` on success. Returns the form with an error message on invalid credentials.

#### Logout

```
GET /logout           — Clear session, redirect to /login
```

### Task Endpoints

#### List All Tasks

```
GET /api/tasks
```

Returns the authenticated user's tasks only.

**Response:** `200 OK`

```json
[
  {
    "id": 1,
    "title": "Review pull request",
    "description": "Check the auth module",
    "status": "pending",
    "created_at": "2026-11-27T09:14:58.435252+00:00",
    "modified_at": "2026-11-27T09:14:58.435252+00:00",
    "subtasks": []
  }
]
```

#### Get Single Task

```
GET /api/tasks/<id>
```

Returns the task only if it belongs to the authenticated user.

**Response:** `200 OK` | `404 Not Found`

#### Create Task

```
POST /api/tasks
```

**Request body:**

| Field         | Type   | Required | Description                        |
|---------------|--------|----------|------------------------------------|
| `title`       | string | Yes      | The task title                     |
| `description` | string | No       | Task description (default: `""`)   |
| `status`      | string | No       | `"pending"` (default) or `"done"`  |

**Response:** `201 Created` | `400 Bad Request`

The task is automatically associated with the logged-in user.

#### Update Task

```
PATCH /api/tasks/<id>
```

**Request body** (all fields optional):

| Field         | Type   | Description              |
|---------------|--------|--------------------------|
| `title`       | string | New task title           |
| `description` | string | New task description     |
| `status`      | string | `"pending"` or `"done"`  |

**Response:** `200 OK` | `404 Not Found`

The `modified_at` field is updated automatically.

#### Delete Task

```
DELETE /api/tasks/<id>
```

**Response:** `204 No Content` | `404 Not Found`

Cascade deletes all subtasks.

### Subtask Endpoints

#### Create Subtask

```
POST /api/tasks/<taskId>/subtasks
```

**Request body:**

| Field    | Type   | Required | Description                        |
|----------|--------|----------|------------------------------------|
| `title`  | string | Yes      | The subtask title                  |
| `status` | string | No       | `"pending"` (default) or `"done"`  |

**Response:** `201 Created` | `404 Not Found` | `400 Bad Request`

Updates the parent task's `modified_at`.

#### Update Subtask

```
PATCH /api/tasks/<taskId>/subtasks/<subId>
```

**Request body** (all fields optional):

| Field    | Type   | Description              |
|----------|--------|--------------------------|
| `title`  | string | New subtask title        |
| `status` | string | `"pending"` or `"done"`  |

**Response:** `200 OK` | `404 Not Found`

Updates the parent task's `modified_at`.

#### Delete Subtask

```
DELETE /api/tasks/<taskId>/subtasks/<subId>
```

**Response:** `204 No Content` | `404 Not Found`

Updates the parent task's `modified_at`.

---

## Pages & Routes

| Route                               | Method    | Auth     | Description                              |
|-------------------------------------|-----------|----------|------------------------------------------|
| `/signup`                           | GET, POST | Public   | Create a new account                     |
| `/login`                            | GET, POST | Public   | Log in to existing account               |
| `/logout`                           | GET       | Public   | Log out and clear session                |
| `/`                                 | GET       | Required | Home page — user's task list             |
| `/task/<id>`                        | GET       | Required | Task detail page — edit, subtasks        |
| `/api/tasks`                        | GET       | Required | API — list user's tasks                  |
| `/api/tasks`                        | POST      | Required | API — create a new task                  |
| `/api/tasks/<id>`                   | GET       | Required | API — get a single task                  |
| `/api/tasks/<id>`                   | PATCH     | Required | API — update a task                      |
| `/api/tasks/<id>`                   | DELETE    | Required | API — delete a task                      |
| `/api/tasks/<id>/subtasks`          | POST      | Required | API — create a subtask                   |
| `/api/tasks/<id>/subtasks/<subId>`  | PATCH     | Required | API — update a subtask                   |
| `/api/tasks/<id>/subtasks/<subId>`  | DELETE    | Required | API — delete a subtask                   |

---

## Project Structure

```
claude-workflow-test/
├── .github/
│   └── workflows/
│       └── ci.yml              # GitHub Actions CI (unit + UI tests in parallel)
├── app.py                      # Flask app, auth, API routes, SQLite database
├── requirements.txt            # Python dependencies
├── tasks.db                    # SQLite database (auto-created, gitignored)
├── test_app.py                 # Unit tests (pytest, 43 tests)
├── test_ui.py                  # UI tests (Selenium + Chrome, 16 tests)
├── static/
│   └── style.css               # All application styles
├── templates/
│   ├── login.html              # Login page
│   ├── signup.html             # Signup page
│   ├── index.html              # Home page — task list and summary
│   └── detail.html             # Task detail page — edit, subtasks
├── README.md                   # Project overview and quick start
├── DOCUMENTATION.md            # This file — full feature documentation
└── TEST_REPORT.md              # Detailed test report with results
```

## Tech Stack

| Component      | Technology                           |
|----------------|--------------------------------------|
| Backend        | Python 3.12, Flask 3.1.0            |
| Database       | SQLite (Python sqlite3 module)       |
| Authentication | Flask sessions, werkzeug password hashing |
| Frontend       | HTML5, CSS3, vanilla JavaScript      |
| Templating     | Jinja2 (via Flask)                  |
| Unit Testing   | pytest 9.2.0                        |
| UI Testing     | Selenium 4.27.1, Chrome (headless)  |
| CI/CD          | GitHub Actions (parallel jobs)       |

## Getting Started

### Prerequisites

- Python 3.10 or later
- Chrome browser (for UI tests only)

### Installation

```bash
pip install -r requirements.txt
```

### Running the App

```bash
python app.py
```

The app starts at **http://localhost:5000** with debug mode enabled. You'll be redirected to the login page — click "Sign up" to create an account.

### First Time Setup

1. Navigate to **http://localhost:5000** — you'll be redirected to `/login`
2. Click **"Sign up"** to create an account
3. Enter a username (unique) and password (minimum 4 characters)
4. After signup, log in with your credentials
5. Start creating tasks!

---

## Testing

The project maintains two test suites that together provide 59 tests covering all features at both the API and browser levels.

### Unit Tests

**File:** `test_app.py`
**Framework:** pytest with Flask test client
**Tests:** 43

Unit tests validate authentication, all API endpoints, per-user task isolation, data model fields, status codes, and error handling. Each test runs in isolation with a fresh temporary SQLite database.

| Test Class        | Tests | Coverage                                                     |
|-------------------|-------|--------------------------------------------------------------|
| TestAuth          | 10    | Signup, login, logout, validation, duplicate username, wrong password, protected routes |
| TestIndex         | 1     | Home page renders with correct content                       |
| TestGetTasks      | 3     | List empty, list after create, per-user isolation            |
| TestGetTask       | 2     | Get existing task with all fields, 404 for nonexistent       |
| TestDetailPage    | 2     | Detail page renders with task data, 404 for nonexistent      |
| TestCreateTask    | 7     | Create with defaults, description, custom status, validation |
| TestUpdateTask    | 5     | Update title, status, description, modified_at, 404          |
| TestDeleteTask    | 3     | Delete returns 204, removes from list, 404                   |
| TestSubtasks      | 10    | Create/toggle/update/delete subtasks, parent timestamp       |

### UI Tests (Selenium)

**File:** `test_ui.py`
**Framework:** pytest + Selenium WebDriver
**Browser:** Chrome (headless mode)
**Tests:** 16

UI tests automate a real browser against a live Flask server to verify end-to-end user workflows. The Flask app runs in a background thread on port 5111 during testing. Each test gets a fresh browser instance.

| Test Class       | Tests | Coverage                                                    |
|------------------|-------|-------------------------------------------------------------|
| TestHomePage     | 6     | Page load, create task, summary bar, toggle, delete, navigation |
| TestDetailPage   | 6     | View task, edit title, edit description, change status, delete, back link |
| TestSubtasksUI   | 4     | Add subtask, toggle subtask, delete subtask, empty placeholder |

### Running Tests

**Unit tests only:**

```bash
pytest test_app.py -v
```

**UI tests only** (requires Chrome):

```bash
pytest test_ui.py -v
```

**All tests:**

```bash
pytest -v
```

### Test Coverage by Feature

| Feature                    | Unit Tests | UI Tests | Total |
|----------------------------|-----------|----------|-------|
| Signup                     | 4         | —        | 4     |
| Login                      | 3         | —        | 3     |
| Logout                     | 1         | —        | 1     |
| Protected route redirect   | 1         | —        | 1     |
| Per-user task isolation    | 1         | —        | 1     |
| Home page rendering        | 1         | 1        | 2     |
| Task list (GET all)        | 2         | 1        | 3     |
| Task detail (GET single)   | 2         | 1        | 3     |
| Detail page rendering      | 2         | 2        | 4     |
| Create task                | 7         | 1        | 8     |
| Update task (title)        | 1         | 1        | 2     |
| Update task (status)       | 2         | 1        | 3     |
| Update task (description)  | 1         | 1        | 2     |
| Update task (modified_at)  | 1         | —        | 1     |
| Delete task                | 3         | 2        | 5     |
| Navigation (links/back)    | —         | 2        | 2     |
| Summary bar                | —         | 1        | 1     |
| Subtask create             | 3         | 1        | 4     |
| Subtask toggle status      | 1         | 1        | 2     |
| Subtask update title       | 1         | —        | 1     |
| Subtask delete             | 2         | 1        | 3     |
| Subtask in parent response | 1         | —        | 1     |
| Subtask parent timestamp   | 1         | —        | 1     |
| Subtask empty placeholder  | —         | 1        | 1     |
| **Total**                  | **43**    | **16**   | **59**|

### Test Architecture

| Aspect           | Unit Tests (`test_app.py`)             | UI Tests (`test_ui.py`)               |
|------------------|----------------------------------------|---------------------------------------|
| What is tested   | Auth, API contracts, data model        | User-facing workflows in a browser    |
| Browser needed   | No                                     | Yes (Chrome)                          |
| Server           | Flask test client (in-process)         | Live Flask server (background thread) |
| Database         | Temporary SQLite file per test         | Shared SQLite for the test session    |
| Speed            | Fast (~0.2s per test)                  | Slower (~7.6s per test)               |
| Isolation        | Fresh database per test                | Fresh browser + data per test         |
| Catches          | Backend logic, auth, validation, 404s  | UI rendering, JS bugs, navigation     |
| Misses           | Frontend JS issues                     | Internal API edge cases               |

---

## CI/CD

GitHub Actions runs both test suites in parallel on every push to `main` and on pull requests. The workflow is defined in `.github/workflows/ci.yml`:

**Job 1: Unit Tests**
1. Checks out the code
2. Sets up Python 3.12
3. Installs dependencies
4. Runs `pytest test_app.py -v`

**Job 2: UI Tests (Selenium)**
1. Checks out the code
2. Sets up Python 3.12
3. Installs dependencies
4. Installs Chrome (stable) via `browser-actions/setup-chrome`
5. Runs `pytest test_ui.py -v`

Both jobs run in parallel for faster CI feedback.
