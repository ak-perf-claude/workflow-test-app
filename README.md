# Workflow Test App

A simple task tracker web application built with Flask for testing Claude workflows.

## Overview

This app lets you create, view, update, and delete tasks through a clean web interface. Each task tracks its status (pending/done) along with created and modified timestamps.

### Features

- **Task Management** — Add, toggle, and delete tasks
- **Status Tracking** — Tasks can be marked as pending or done
- **Timestamps** — Each task records its created date and last modified date
- **Summary Bar** — Displays total, pending, and done task counts at a glance
- **REST API** — Full CRUD API for programmatic access

## Tech Stack

- **Backend:** Python / Flask
- **Frontend:** HTML, CSS, vanilla JavaScript
- **Storage:** In-memory (resets on server restart)

## Getting Started

### Prerequisites

- Python 3.10+

### Installation

```bash
pip install -r requirements.txt
```

### Running the App

```bash
python app.py
```

The app will be available at **http://localhost:5000**.

## API Endpoints

| Method   | Endpoint              | Description          |
|----------|-----------------------|----------------------|
| `GET`    | `/`                   | Web UI               |
| `GET`    | `/api/tasks`          | List all tasks       |
| `POST`   | `/api/tasks`          | Create a task        |
| `PATCH`  | `/api/tasks/<id>`     | Update a task        |
| `DELETE` | `/api/tasks/<id>`     | Delete a task        |

### Example: Create a Task

```bash
curl -X POST http://localhost:5000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "My first task"}'
```

## Project Structure

```
claude-workflow-test/
├── app.py              # Flask application and API routes
├── requirements.txt    # Python dependencies
├── static/
│   └── style.css       # Stylesheet
└── templates/
    └── index.html      # Web UI template
```
