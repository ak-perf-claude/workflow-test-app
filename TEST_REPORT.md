# Test Report — Workflow Test App

**Date:** 2026-11-27
**Environment:** Windows 11 Enterprise, Python 3.12.10, Flask 3.1.0
**Browser:** Chrome (headless) via Selenium 4.27.1
**Test Framework:** pytest 9.2.0

---

## Summary

| Suite          | File           | Tests | Passed | Failed | Duration |
|----------------|----------------|-------|--------|--------|----------|
| Unit Tests     | `test_app.py`  | 32    | 32     | 0      | 0.83s    |
| UI Tests       | `test_ui.py`   | 16    | 16     | 0      | 121.68s  |
| **Total**      |                | **48**| **48** | **0**  |          |

**Result: ALL TESTS PASSED**

---

## Unit Tests (`test_app.py`)

Unit tests use the Flask test client to validate all API endpoints and page routes without a browser. Each test runs in isolation with a clean in-memory task list.

### TestIndex (1 test)

| # | Test | Description | Result |
|---|------|-------------|--------|
| 1 | `test_index_returns_html` | GET `/` returns 200 and contains "Workflow Test App" | PASSED |

### TestGetTasks (2 tests)

| # | Test | Description | Result |
|---|------|-------------|--------|
| 2 | `test_empty_list` | GET `/api/tasks` returns 200 with empty array | PASSED |
| 3 | `test_list_after_create` | GET `/api/tasks` returns created tasks in order | PASSED |

### TestGetTask (2 tests)

| # | Test | Description | Result |
|---|------|-------------|--------|
| 4 | `test_get_existing_task` | GET `/api/tasks/1` returns correct task with all fields | PASSED |
| 5 | `test_get_nonexistent_returns_404` | GET `/api/tasks/999` returns 404 | PASSED |

### TestDetailPage (2 tests)

| # | Test | Description | Result |
|---|------|-------------|--------|
| 6 | `test_detail_page_returns_html` | GET `/task/1` returns HTML with task title and "Task #1" | PASSED |
| 7 | `test_detail_page_nonexistent_returns_404` | GET `/task/999` returns 404 | PASSED |

### TestCreateTask (7 tests)

| # | Test | Description | Result |
|---|------|-------------|--------|
| 8 | `test_create_returns_201` | POST `/api/tasks` with valid title returns 201 | PASSED |
| 9 | `test_create_sets_fields` | Created task has correct title, description, status, subtasks, and timestamps | PASSED |
| 10 | `test_create_with_custom_status` | POST with `status: "done"` sets status correctly | PASSED |
| 11 | `test_create_with_description` | POST with `description` field stores it | PASSED |
| 12 | `test_create_default_description` | POST without description defaults to empty string | PASSED |
| 13 | `test_create_missing_title_returns_400` | POST with empty JSON body returns 400 | PASSED |
| 14 | `test_create_no_body_returns_400` | POST with no body returns 400 | PASSED |

### TestUpdateTask (5 tests)

| # | Test | Description | Result |
|---|------|-------------|--------|
| 15 | `test_update_title` | PATCH with new title updates and returns it | PASSED |
| 16 | `test_update_status` | PATCH with new status updates and returns it | PASSED |
| 17 | `test_update_changes_modified_at` | PATCH updates `modified_at` timestamp | PASSED |
| 18 | `test_update_description` | PATCH with description updates and returns it | PASSED |
| 19 | `test_update_nonexistent_returns_404` | PATCH on nonexistent task returns 404 | PASSED |

### TestDeleteTask (3 tests)

| # | Test | Description | Result |
|---|------|-------------|--------|
| 20 | `test_delete_returns_204` | DELETE `/api/tasks/1` returns 204 | PASSED |
| 21 | `test_delete_removes_task` | Deleted task no longer appears in GET list | PASSED |
| 22 | `test_delete_nonexistent_returns_404` | DELETE on nonexistent task returns 404 | PASSED |

### TestSubtasks (10 tests)

| # | Test | Description | Result |
|---|------|-------------|--------|
| 23 | `test_create_subtask` | POST `/api/tasks/1/subtasks` returns 201 with correct fields | PASSED |
| 24 | `test_create_subtask_missing_title` | POST subtask without title returns 400 | PASSED |
| 25 | `test_create_subtask_nonexistent_task` | POST subtask on nonexistent task returns 404 | PASSED |
| 26 | `test_subtask_in_task_response` | Created subtasks appear in parent task GET response | PASSED |
| 27 | `test_toggle_subtask_status` | PATCH subtask status to "done" updates correctly | PASSED |
| 28 | `test_update_subtask_title` | PATCH subtask with new title updates correctly | PASSED |
| 29 | `test_update_nonexistent_subtask` | PATCH nonexistent subtask returns 404 | PASSED |
| 30 | `test_delete_subtask` | DELETE subtask returns 204 and removes it from parent | PASSED |
| 31 | `test_delete_nonexistent_subtask` | DELETE nonexistent subtask returns 404 | PASSED |
| 32 | `test_subtask_updates_parent_modified_at` | Subtask create updates parent `modified_at` | PASSED |

---

## UI Tests (`test_ui.py`)

UI tests use Selenium WebDriver with headless Chrome to automate a real browser against a live Flask server. They verify end-to-end user workflows through the actual web interface.

### TestHomePage (6 tests)

| # | Test | Description | Result |
|---|------|-------------|--------|
| 1 | `test_page_loads` | Home page loads with correct title | PASSED |
| 2 | `test_create_task` | Type a task name, click Add, task appears in list | PASSED |
| 3 | `test_summary_bar_updates` | Summary bar shows Total/Pending counts after adding a task | PASSED |
| 4 | `test_toggle_task_status` | Click Toggle button changes task status to "done" | PASSED |
| 5 | `test_delete_task` | Click Delete button removes the task from the list | PASSED |
| 6 | `test_task_title_links_to_detail` | Clicking task title navigates to `/task/<id>` detail page | PASSED |

### TestDetailPage (6 tests)

| # | Test | Description | Result |
|---|------|-------------|--------|
| 7 | `test_detail_page_shows_task` | Detail page displays the correct task title in the input | PASSED |
| 8 | `test_edit_title` | Edit title, click Save Changes, success message appears | PASSED |
| 9 | `test_edit_description` | Edit description textarea, click Save Changes, value persists | PASSED |
| 10 | `test_change_status` | Change status dropdown to "Done", save, badge updates | PASSED |
| 11 | `test_delete_redirects_home` | Click Delete Task, accept confirmation, redirects to home page | PASSED |
| 12 | `test_back_link` | Click "Back to tasks" link navigates to home page | PASSED |

### TestSubtasksUI (4 tests)

| # | Test | Description | Result |
|---|------|-------------|--------|
| 13 | `test_add_subtask` | Type subtask name, click Add, subtask appears in list | PASSED |
| 14 | `test_toggle_subtask` | Click Toggle on a subtask changes its status to "done" | PASSED |
| 15 | `test_delete_subtask` | Click Delete on a subtask removes it from the list | PASSED |
| 16 | `test_no_subtasks_placeholder` | "No subtasks yet." placeholder visible when list is empty | PASSED |

---

## Test Coverage by Feature

| Feature | Unit Tests | UI Tests | Total |
|---------|-----------|----------|-------|
| Home page rendering | 1 | 1 | 2 |
| Task list (GET all) | 2 | 1 | 3 |
| Task detail (GET single) | 2 | 1 | 3 |
| Detail page rendering | 2 | 2 | 4 |
| Create task | 7 | 1 | 8 |
| Update task (title) | 1 | 1 | 2 |
| Update task (status) | 2 | 1 | 3 |
| Update task (description) | 1 | 1 | 2 |
| Update task (modified_at) | 1 | — | 1 |
| Delete task | 3 | 2 | 5 |
| Navigation (links/back) | — | 2 | 2 |
| Summary bar | — | 1 | 1 |
| Subtask create | 3 | 1 | 4 |
| Subtask toggle status | 1 | 1 | 2 |
| Subtask update title | 1 | — | 1 |
| Subtask delete | 2 | 1 | 3 |
| Subtask in parent response | 1 | — | 1 |
| Subtask updates parent timestamp | 1 | — | 1 |
| Subtask empty placeholder | — | 1 | 1 |
| **Total** | **32** | **16** | **48** |

---

## How to Run

### Unit Tests

```bash
pytest test_app.py -v
```

### UI Tests

Requires Chrome and ChromeDriver installed.

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
- **Isolation:** Each test resets the in-memory `tasks` list via fixture
- **Approach:** Direct HTTP calls to API endpoints, asserting status codes and JSON response bodies
- **Speed:** ~0.83 seconds for 32 tests

### UI Tests (`test_ui.py`)

- **Framework:** pytest + Selenium WebDriver
- **Browser:** Chrome in headless mode
- **Server:** Flask runs in a background thread on port 5111
- **Isolation:** Each test gets a fresh browser instance; task list is cleared between tests
- **Waits:** Explicit waits (`WebDriverWait`) for dynamic DOM updates after async fetch calls
- **Speed:** ~122 seconds for 16 tests (browser startup/teardown overhead)

### Key Differences

| Aspect | Unit Tests | UI Tests |
|--------|-----------|----------|
| What is tested | API contracts, data model | User-facing workflows |
| Browser needed | No | Yes (Chrome) |
| Speed | Fast (~0.03s/test) | Slower (~7.6s/test) |
| Catches | Backend logic bugs, 404/400 errors | UI rendering, JS bugs, navigation |
| Misses | Frontend JS issues | Internal API edge cases |
