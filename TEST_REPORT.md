# Test Report — Workflow Test App

**Date:** 2026-11-27
**Environment:** Windows 11 Enterprise, Python 3.12.10, Flask 3.1.0
**Database:** SQLite (temporary file per unit test, shared file for UI tests)
**Browser:** Chrome (headless) via Selenium 4.27.1
**Test Framework:** pytest 9.2.0

---

## Summary

| Suite          | File           | Tests  | Passed | Failed | Duration |
|----------------|----------------|--------|--------|--------|----------|
| Unit Tests     | `test_app.py`  | 43     | 43     | 0      | ~9s      |
| UI Tests       | `test_ui.py`   | 25     | 25     | 0      | ~180s    |
| **Total**      |                | **68** | **68** | **0**  |          |

**Result: ALL TESTS PASSED**

---

## Unit Tests (`test_app.py`)

Unit tests use the Flask test client with a temporary SQLite database to validate all API endpoints, authentication, and per-user task isolation. Each test runs in isolation with a fresh database.

### TestAuth (10 tests)

| # | Test | Description | Result |
|---|------|-------------|--------|
| 1 | `test_signup_page_loads` | GET `/signup` returns 200 with "Sign Up" | PASSED |
| 2 | `test_login_page_loads` | GET `/login` returns 200 with "Log In" | PASSED |
| 3 | `test_signup_and_login` | Register then login succeeds, shows home page | PASSED |
| 4 | `test_signup_duplicate_username` | Duplicate username returns "already taken" error | PASSED |
| 5 | `test_signup_password_mismatch` | Mismatched passwords returns "do not match" error | PASSED |
| 6 | `test_signup_short_password` | Short password returns "at least 4" error | PASSED |
| 7 | `test_login_wrong_password` | Wrong password returns "Invalid" error | PASSED |
| 8 | `test_login_nonexistent_user` | Nonexistent user returns "Invalid" error | PASSED |
| 9 | `test_logout_redirects_to_login` | Logout clears session and shows login page | PASSED |
| 10 | `test_protected_route_redirects` | Unauthenticated GET `/` redirects to login | PASSED |

### TestIndex (1 test)

| # | Test | Description | Result |
|---|------|-------------|--------|
| 11 | `test_index_returns_html` | GET `/` (logged in) returns 200 with "Workflow Test App" | PASSED |

### TestGetTasks (3 tests)

| # | Test | Description | Result |
|---|------|-------------|--------|
| 12 | `test_empty_list` | GET `/api/tasks` returns 200 with empty array | PASSED |
| 13 | `test_list_after_create` | GET `/api/tasks` returns created tasks in order | PASSED |
| 14 | `test_tasks_are_per_user` | User A's tasks are not visible to User B | PASSED |

### TestGetTask (2 tests)

| # | Test | Description | Result |
|---|------|-------------|--------|
| 15 | `test_get_existing_task` | GET `/api/tasks/1` returns correct task with all fields | PASSED |
| 16 | `test_get_nonexistent_returns_404` | GET `/api/tasks/999` returns 404 | PASSED |

### TestDetailPage (2 tests)

| # | Test | Description | Result |
|---|------|-------------|--------|
| 17 | `test_detail_page_returns_html` | GET `/task/1` returns HTML with task title and "Task #1" | PASSED |
| 18 | `test_detail_page_nonexistent_returns_404` | GET `/task/999` returns 404 | PASSED |

### TestCreateTask (7 tests)

| # | Test | Description | Result |
|---|------|-------------|--------|
| 19 | `test_create_returns_201` | POST `/api/tasks` with valid title returns 201 | PASSED |
| 20 | `test_create_sets_fields` | Created task has correct title, description, status, subtasks, timestamps | PASSED |
| 21 | `test_create_with_custom_status` | POST with `status: "done"` sets status correctly | PASSED |
| 22 | `test_create_with_description` | POST with `description` field stores it | PASSED |
| 23 | `test_create_default_description` | POST without description defaults to empty string | PASSED |
| 24 | `test_create_missing_title_returns_400` | POST with empty JSON body returns 400 | PASSED |
| 25 | `test_create_no_body_returns_400` | POST with no body returns 400 | PASSED |

### TestUpdateTask (5 tests)

| # | Test | Description | Result |
|---|------|-------------|--------|
| 26 | `test_update_title` | PATCH with new title updates and returns it | PASSED |
| 27 | `test_update_status` | PATCH with new status updates and returns it | PASSED |
| 28 | `test_update_changes_modified_at` | PATCH updates `modified_at` timestamp | PASSED |
| 29 | `test_update_description` | PATCH with description updates and returns it | PASSED |
| 30 | `test_update_nonexistent_returns_404` | PATCH on nonexistent task returns 404 | PASSED |

### TestDeleteTask (3 tests)

| # | Test | Description | Result |
|---|------|-------------|--------|
| 31 | `test_delete_returns_204` | DELETE `/api/tasks/1` returns 204 | PASSED |
| 32 | `test_delete_removes_task` | Deleted task no longer appears in GET list | PASSED |
| 33 | `test_delete_nonexistent_returns_404` | DELETE on nonexistent task returns 404 | PASSED |

### TestSubtasks (10 tests)

| # | Test | Description | Result |
|---|------|-------------|--------|
| 34 | `test_create_subtask` | POST subtask returns 201 with correct fields | PASSED |
| 35 | `test_create_subtask_missing_title` | POST subtask without title returns 400 | PASSED |
| 36 | `test_create_subtask_nonexistent_task` | POST subtask on nonexistent task returns 404 | PASSED |
| 37 | `test_subtask_in_task_response` | Created subtasks appear in parent task GET response | PASSED |
| 38 | `test_toggle_subtask_status` | PATCH subtask status to "done" updates correctly | PASSED |
| 39 | `test_update_subtask_title` | PATCH subtask with new title updates correctly | PASSED |
| 40 | `test_update_nonexistent_subtask` | PATCH nonexistent subtask returns 404 | PASSED |
| 41 | `test_delete_subtask` | DELETE subtask returns 204 and removes it from parent | PASSED |
| 42 | `test_delete_nonexistent_subtask` | DELETE nonexistent subtask returns 404 | PASSED |
| 43 | `test_subtask_updates_parent_modified_at` | Subtask create updates parent `modified_at` | PASSED |

---

## UI Tests (`test_ui.py`)

UI tests use Selenium WebDriver with headless Chrome to automate a real browser against a live Flask server with SQLite. They verify end-to-end user workflows including authentication.

### TestAuthUI (6 tests)

| # | Test | Description | Result |
|---|------|-------------|--------|
| 1 | `test_redirect_to_login` | Unauthenticated visit to `/` redirects to `/login` | PASSED |
| 2 | `test_signup_page_loads` | Signup page loads with correct title | PASSED |
| 3 | `test_login_page_loads` | Login page loads with correct title | PASSED |
| 4 | `test_signup_and_login_flow` | Full signup then login flow, nav bar shows username | PASSED |
| 5 | `test_logout` | Clicking Logout redirects to login page | PASSED |
| 6 | `test_login_wrong_password` | Invalid login shows error message | PASSED |

### TestHomePage (6 tests)

| # | Test | Description | Result |
|---|------|-------------|--------|
| 7 | `test_page_loads` | Home page loads with correct title after login | PASSED |
| 8 | `test_create_task` | Type a task name, click Add, task appears in list | PASSED |
| 9 | `test_summary_bar_updates` | Summary bar shows Total/Pending counts after adding a task | PASSED |
| 10 | `test_toggle_task_status` | Click Toggle button changes task status to "done" | PASSED |
| 11 | `test_delete_task` | Click Delete button removes the task from the list | PASSED |
| 12 | `test_task_title_links_to_detail` | Clicking task title navigates to detail page | PASSED |

### TestDetailPage (7 tests)

| # | Test | Description | Result |
|---|------|-------------|--------|
| 13 | `test_detail_page_shows_task` | Detail page displays the correct task title | PASSED |
| 14 | `test_edit_title` | Edit title, click Save, success message appears | PASSED |
| 15 | `test_edit_description` | Edit description, click Save, value persists | PASSED |
| 16 | `test_change_status` | Change status dropdown to "Done", save, badge updates | PASSED |
| 17 | `test_delete_redirects_home` | Click Delete, accept confirmation, redirects to home | PASSED |
| 18 | `test_back_link` | Click "Back to tasks" navigates to home page | PASSED |
| 19 | `test_nav_bar_shows_username` | Nav bar displays "Logged in as" with username | PASSED |

### TestSubtasksUI (4 tests)

| # | Test | Description | Result |
|---|------|-------------|--------|
| 20 | `test_add_subtask` | Type subtask name, click Add, subtask appears | PASSED |
| 21 | `test_toggle_subtask` | Click Toggle on subtask changes status to "done" | PASSED |
| 22 | `test_delete_subtask` | Click Delete on subtask removes it | PASSED |
| 23 | `test_no_subtasks_placeholder` | "No subtasks yet." visible when list is empty | PASSED |

---

## Test Coverage by Feature

| Feature                    | Unit Tests | UI Tests | Total |
|----------------------------|-----------|----------|-------|
| Signup (validation)        | 4         | 2        | 6     |
| Login (validation)         | 3         | 2        | 5     |
| Logout                     | 1         | 1        | 2     |
| Protected route redirect   | 1         | 1        | 2     |
| Per-user task isolation    | 1         | —        | 1     |
| Nav bar (username display) | —         | 1        | 1     |
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
| **Total**                  | **43**    | **25**   | **68**|

---

## How to Run

### Unit Tests

```bash
pytest test_app.py -v
```

### UI Tests

Requires Chrome browser and ChromeDriver.

```bash
pytest test_ui.py -v
```

### All Tests

```bash
pytest -v
```

---

## Test Architecture

### Unit Tests (`test_app.py`)

- **Framework:** pytest with Flask test client
- **Database:** Temporary SQLite file per test (cleaned up after)
- **Auth:** Each test registers and logs in a user via helper functions
- **Isolation:** Fresh database per test — no state leaks
- **Speed:** ~9 seconds for 43 tests

### UI Tests (`test_ui.py`)

- **Framework:** pytest + Selenium WebDriver
- **Browser:** Chrome in headless mode
- **Server:** Flask runs in a background thread on port 5111 with SQLite
- **Auth:** Each test creates a unique user via the signup/login UI flow
- **Isolation:** Fresh user per test — each user starts with zero tasks
- **Speed:** ~180 seconds for 25 tests (browser startup/teardown overhead)

### Key Differences

| Aspect           | Unit Tests (`test_app.py`)             | UI Tests (`test_ui.py`)               |
|------------------|----------------------------------------|---------------------------------------|
| What is tested   | Auth, API contracts, data model        | Auth flow, browser workflows, navigation |
| Browser needed   | No                                     | Yes (Chrome)                          |
| Server           | Flask test client (in-process)         | Live Flask server (background thread) |
| Database         | Temporary SQLite file per test         | Shared SQLite for the test session    |
| Auth isolation   | Fresh DB per test                      | Unique user per test                  |
| Speed            | Fast (~0.2s per test)                  | Slower (~7s per test)                 |
| Catches          | Backend logic, auth, validation, 404s  | UI rendering, JS bugs, auth flow, navigation |
| Misses           | Frontend JS issues                     | Internal API edge cases               |
