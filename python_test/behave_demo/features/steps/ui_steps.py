from behave import given, when, then
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time


@given("browser is open")
def step_open_browser(context):
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")

    service = Service("/Users/liangchang/code/frameworks_convert/chromedriver/chromedriver")
    context.driver = webdriver.Chrome(service=service, options=chrome_options)


@when("I open login page")
def step_open_login(context):
    context.driver.get("http://127.0.0.1:5000/login")


@when('I login via ui with username "{u}" and password "{p}"')
def step_login_ui(context, u, p):
    d = context.driver
    d.find_element(By.ID, "username").send_keys(u)
    d.find_element(By.ID, "password").send_keys(p)
    d.find_element(By.ID, "loginBtn").click()


@then("I should see dashboard")
def step_dashboard(context):
    time.sleep(1)
    assert "/dashboard" in context.driver.current_url
    context.driver.quit()


@when("I open register page")
def step_open_register(context):
    context.driver.get("http://127.0.0.1:5000/register")


@when("I register random user via ui")
def step_register_ui(context):
    context.temp_user = f"user{int(time.time())}"
    d = context.driver
    d.find_element(By.ID, "username").send_keys(context.temp_user)
    d.find_element(By.ID, "password").send_keys("123456")
    d.find_element(By.ID, "registerBtn").click()


@then("I should go to login page")
def step_go_login(context):
    time.sleep(1)
    assert "/login" in context.driver.current_url
    context.driver.quit()


@when("I login as admin via ui")
def step_login_admin(context):
    d = context.driver
    d.get("http://127.0.0.1:5000/login")
    d.find_element(By.ID, "username").send_keys("admin")
    d.find_element(By.ID, "password").send_keys("123456")
    d.find_element(By.ID, "loginBtn").click()


@when("I delete user via ui")
def step_delete_user(context):
    d = context.driver
    d.get("http://127.0.0.1:5000/users")
    d.find_element(By.CSS_SELECTOR, "a[href^='/delete/']").click()


@then("I should see delete success")
def step_delete_success(context):
    time.sleep(1)
    assert "删除成功" in context.driver.page_source
    context.driver.quit()