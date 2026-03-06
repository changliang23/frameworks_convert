import requests
import time
import pytest
from pytest_bdd import scenarios, given, when, then, parsers

BASE_URL = "http://127.0.0.1:5000"

scenarios("../features/api.feature")

@pytest.fixture
def context():
    return {}

@given("API server is running")
def api_running():
    pass


@when("I register a new user")
def register(context):
    username = "user" + str(int(time.time()))
    body = {
        "username": username,
        "password": "123456"
    }

    r = requests.post(f"{BASE_URL}/api/register", json=body)

    context["response"] = r
    context["username"] = username


@then("register response should be success")
def register_success(context):
    r = context["response"]
    assert r.status_code == 200
    assert r.json()["msg"] == "register success"


@when(parsers.parse('I login with username "{username}" and password "{password}"'))
def login(context, username, password):

    body = {
        "username": username,
        "password": password
    }

    r = requests.post(f"{BASE_URL}/api/login", json=body)

    context["response"] = r


@then(parsers.parse('login response should be "{msg}"'))
def login_check(context, msg):

    r = context["response"]

    assert r.json()["msg"] == msg


@when("I get user list")
def get_users(context):

    r = requests.get(f"{BASE_URL}/api/users")

    context["response"] = r


@then("user list should not be empty")
def check_users(context):

    r = context["response"]

    assert len(r.json()["users"]) > 0