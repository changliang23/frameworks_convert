import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from selenium import webdriver
from selenium.webdriver.common.by import By

scenarios("../features/ui.feature")

@pytest.fixture
def driver():
    driver = webdriver.Chrome()
    yield driver
    driver.quit()


@given("browser is open")
def browser_open(driver):
    pass


@when("I open login page")
def open_login(driver):
    driver.get("http://127.0.0.1:5000/login")


@when(parsers.parse('I login with username "{username}" and password "{password}"'))
def login(driver, username, password):

    driver.find_element(By.ID,"username").send_keys(username)
    driver.find_element(By.ID,"password").send_keys(password)

    driver.find_element(By.ID,"loginBtn").click()


@then("I should see dashboard")
def check_dashboard(driver):

    assert "/dashboard" in driver.current_url