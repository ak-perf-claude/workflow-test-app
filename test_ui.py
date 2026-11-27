import os
import tempfile
import threading
import time

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

from app import app, init_db

BASE_URL = "http://127.0.0.1:5111"
TEST_USER = "uitester"
TEST_PASS = "testpass"


@pytest.fixture(scope="module")
def server():
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    app.config["TESTING"] = True
    app.config["DATABASE"] = db_path
    app.config["SECRET_KEY"] = "ui-test-secret"
    with app.app_context():
        init_db()
    server = threading.Thread(
        target=lambda: app.run(port=5111, use_reloader=False),
        daemon=True,
    )
    server.start()
    time.sleep(1)
    yield
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def driver(server):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    d = webdriver.Chrome(options=options)
    d.implicitly_wait(5)
    yield d
    d.quit()


def wait_for(driver, by, value, timeout=5):
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by, value))
    )


def signup_ui(driver, username=TEST_USER, password=TEST_PASS):
    driver.get(f"{BASE_URL}/signup")
    driver.find_element(By.ID, "username").send_keys(username)
    driver.find_element(By.ID, "password").send_keys(password)
    driver.find_element(By.ID, "confirm").send_keys(password)
    driver.find_element(By.CSS_SELECTOR, ".auth-form button").click()
    wait_for(driver, By.CSS_SELECTOR, ".auth-form")


def login_ui(driver, username=TEST_USER, password=TEST_PASS):
    driver.get(f"{BASE_URL}/login")
    driver.find_element(By.ID, "username").send_keys(username)
    driver.find_element(By.ID, "password").send_keys(password)
    driver.find_element(By.CSS_SELECTOR, ".auth-form button").click()
    wait_for(driver, By.ID, "task-form")


import uuid


def fresh_login(driver):
    username = f"ui_{uuid.uuid4().hex[:8]}"
    signup_ui(driver, username, TEST_PASS)
    login_ui(driver, username, TEST_PASS)


class TestAuthUI:
    def test_redirect_to_login(self, driver):
        driver.get(BASE_URL)
        WebDriverWait(driver, 5).until(EC.url_contains("/login"))
        assert "/login" in driver.current_url

    def test_signup_page_loads(self, driver):
        driver.get(f"{BASE_URL}/signup")
        assert "Sign Up" in driver.title

    def test_login_page_loads(self, driver):
        driver.get(f"{BASE_URL}/login")
        assert "Log In" in driver.title

    def test_signup_and_login_flow(self, driver):
        fresh_login(driver)
        assert "Workflow Test App" in driver.title
        nav = driver.find_element(By.CSS_SELECTOR, ".nav-bar")
        assert "Logged in as" in nav.text

    def test_logout(self, driver):
        fresh_login(driver)
        driver.find_element(By.CSS_SELECTOR, ".nav-bar a").click()
        WebDriverWait(driver, 5).until(EC.url_contains("/login"))
        assert "/login" in driver.current_url

    def test_login_wrong_password(self, driver):
        driver.get(f"{BASE_URL}/login")
        driver.find_element(By.ID, "username").send_keys("nonexistent")
        driver.find_element(By.ID, "password").send_keys("wrong")
        driver.find_element(By.CSS_SELECTOR, ".auth-form button").click()
        wait_for(driver, By.CSS_SELECTOR, ".message.error")
        error = driver.find_element(By.CSS_SELECTOR, ".message.error")
        assert "Invalid" in error.text


class TestHomePage:
    def test_page_loads(self, driver):
        fresh_login(driver)
        assert "Workflow Test App" in driver.title

    def test_create_task(self, driver):
        fresh_login(driver)
        inp = driver.find_element(By.ID, "task-input")
        inp.send_keys("Selenium task")
        driver.find_element(By.CSS_SELECTOR, "#task-form button").click()
        wait_for(driver, By.CSS_SELECTOR, ".task")
        tasks = driver.find_elements(By.CSS_SELECTOR, ".task")
        assert any("Selenium task" in t.text for t in tasks)

    def test_summary_bar_updates(self, driver):
        fresh_login(driver)
        inp = driver.find_element(By.ID, "task-input")
        inp.send_keys("Summary test")
        driver.find_element(By.CSS_SELECTOR, "#task-form button").click()
        wait_for(driver, By.CSS_SELECTOR, ".summary-item")
        summary = driver.find_element(By.ID, "task-summary").text
        assert "Total:" in summary
        assert "Pending:" in summary

    def test_toggle_task_status(self, driver):
        fresh_login(driver)
        inp = driver.find_element(By.ID, "task-input")
        inp.send_keys("Toggle test")
        driver.find_element(By.CSS_SELECTOR, "#task-form button").click()
        wait_for(driver, By.CSS_SELECTOR, ".task")
        toggle_btn = driver.find_element(By.XPATH, "//button[text()='Toggle']")
        toggle_btn.click()
        time.sleep(0.5)
        status = driver.find_element(By.CSS_SELECTOR, ".task .status")
        assert "done" in status.text.lower()

    def test_delete_task(self, driver):
        fresh_login(driver)
        inp = driver.find_element(By.ID, "task-input")
        inp.send_keys("Delete me")
        driver.find_element(By.CSS_SELECTOR, "#task-form button").click()
        wait_for(driver, By.CSS_SELECTOR, ".task")
        delete_btn = driver.find_element(By.XPATH, "//button[text()='Delete']")
        delete_btn.click()
        time.sleep(0.5)
        tasks = driver.find_elements(By.CSS_SELECTOR, ".task")
        assert not any("Delete me" in t.text for t in tasks)

    def test_task_title_links_to_detail(self, driver):
        fresh_login(driver)
        inp = driver.find_element(By.ID, "task-input")
        inp.send_keys("Link test")
        driver.find_element(By.CSS_SELECTOR, "#task-form button").click()
        wait_for(driver, By.CSS_SELECTOR, "a.title")
        link = driver.find_element(By.CSS_SELECTOR, "a.title")
        link.click()
        wait_for(driver, By.CSS_SELECTOR, ".detail-card")
        assert "/task/" in driver.current_url


class TestDetailPage:
    def _create_and_navigate(self, driver, title="Detail test"):
        fresh_login(driver)
        inp = driver.find_element(By.ID, "task-input")
        inp.send_keys(title)
        driver.find_element(By.CSS_SELECTOR, "#task-form button").click()
        wait_for(driver, By.CSS_SELECTOR, "a.title")
        driver.find_element(By.CSS_SELECTOR, "a.title").click()
        wait_for(driver, By.CSS_SELECTOR, ".detail-card")

    def test_detail_page_shows_task(self, driver):
        self._create_and_navigate(driver, "Detail view")
        title_input = driver.find_element(By.ID, "title-input")
        assert title_input.get_attribute("value") == "Detail view"

    def test_edit_title(self, driver):
        self._create_and_navigate(driver, "Old name")
        title_input = driver.find_element(By.ID, "title-input")
        title_input.clear()
        title_input.send_keys("New name")
        driver.find_element(By.CSS_SELECTOR, ".btn-save").click()
        wait_for(driver, By.CSS_SELECTOR, ".message.success")
        msg = driver.find_element(By.ID, "message").text
        assert "updated" in msg.lower()

    def test_edit_description(self, driver):
        self._create_and_navigate(driver, "Desc test")
        textarea = driver.find_element(By.ID, "desc-input")
        textarea.clear()
        textarea.send_keys("My description text")
        driver.find_element(By.CSS_SELECTOR, ".btn-save").click()
        wait_for(driver, By.CSS_SELECTOR, ".message.success")
        time.sleep(0.5)
        updated = driver.find_element(By.ID, "desc-input")
        actual = updated.get_attribute("value") or updated.text
        assert "My description text" in actual

    def test_change_status(self, driver):
        self._create_and_navigate(driver, "Status test")
        select = Select(driver.find_element(By.ID, "status-select"))
        select.select_by_value("done")
        driver.find_element(By.CSS_SELECTOR, ".btn-save").click()
        wait_for(driver, By.CSS_SELECTOR, ".message.success")
        badge = driver.find_element(By.ID, "status-badge")
        assert "done" in badge.text.lower()

    def test_delete_redirects_home(self, driver):
        self._create_and_navigate(driver, "Delete from detail")
        driver.find_element(By.CSS_SELECTOR, ".btn-delete").click()
        WebDriverWait(driver, 3).until(EC.alert_is_present())
        driver.switch_to.alert.accept()
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "task-form"))
        )
        time.sleep(0.5)

    def test_back_link(self, driver):
        self._create_and_navigate(driver, "Back link test")
        detail_url = driver.current_url
        assert "/task/" in detail_url
        back = driver.find_element(By.CSS_SELECTOR, ".back-link")
        back.click()
        WebDriverWait(driver, 10).until(EC.url_changes(detail_url))
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "task-form"))
        )
        assert "/task/" not in driver.current_url

    def test_nav_bar_shows_username(self, driver):
        self._create_and_navigate(driver, "Nav test")
        nav = driver.find_element(By.CSS_SELECTOR, ".nav-bar")
        assert "Logged in as" in nav.text


class TestSubtasksUI:
    def _create_and_navigate(self, driver, title="Subtask parent"):
        fresh_login(driver)
        inp = driver.find_element(By.ID, "task-input")
        inp.send_keys(title)
        driver.find_element(By.CSS_SELECTOR, "#task-form button").click()
        wait_for(driver, By.CSS_SELECTOR, "a.title")
        driver.find_element(By.CSS_SELECTOR, "a.title").click()
        wait_for(driver, By.CSS_SELECTOR, ".subtasks-card")

    def test_add_subtask(self, driver):
        self._create_and_navigate(driver)
        inp = driver.find_element(By.ID, "subtask-input")
        inp.send_keys("My subtask")
        driver.find_element(By.CSS_SELECTOR, ".subtask-add-form button").click()
        wait_for(driver, By.CSS_SELECTOR, ".subtask")
        subtasks = driver.find_elements(By.CSS_SELECTOR, ".subtask")
        assert len(subtasks) == 1
        assert "My subtask" in subtasks[0].text

    def test_toggle_subtask(self, driver):
        self._create_and_navigate(driver)
        inp = driver.find_element(By.ID, "subtask-input")
        inp.send_keys("Toggle sub")
        driver.find_element(By.CSS_SELECTOR, ".subtask-add-form button").click()
        wait_for(driver, By.CSS_SELECTOR, ".subtask")
        toggle_btn = driver.find_element(
            By.CSS_SELECTOR, ".subtask .actions button:first-child"
        )
        toggle_btn.click()
        time.sleep(0.5)
        status = driver.find_element(By.CSS_SELECTOR, ".subtask .status")
        assert "done" in status.text.lower()

    def test_delete_subtask(self, driver):
        self._create_and_navigate(driver)
        inp = driver.find_element(By.ID, "subtask-input")
        inp.send_keys("Delete sub")
        driver.find_element(By.CSS_SELECTOR, ".subtask-add-form button").click()
        wait_for(driver, By.CSS_SELECTOR, ".subtask")
        delete_btn = driver.find_element(
            By.CSS_SELECTOR, ".subtask .actions button:last-child"
        )
        delete_btn.click()
        time.sleep(0.5)
        subtasks = driver.find_elements(By.CSS_SELECTOR, ".subtask")
        assert len(subtasks) == 0

    def test_no_subtasks_placeholder(self, driver):
        self._create_and_navigate(driver)
        empty = driver.find_element(By.ID, "subtask-empty")
        assert empty.is_displayed()
        assert "No subtasks yet" in empty.text
