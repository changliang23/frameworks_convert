from behave import given, when, then
import requests
import time

BASE_URL = "http://127.0.0.1:5000"


@given("API server is running")
def step_api_server(context):
    context.base_url = BASE_URL


@when("I register via api")
def step_register_api(context):
    context.temp_user = f"user{int(time.time())}"
    payload = {
        "username": context.temp_user,
        "password": "123456"
    }
    context.response = requests.post(
        f"{context.base_url}/api/register",
        json=payload
    )


@then("api register response should be success")
def step_register_success(context):
    assert context.response.status_code == 200
    assert context.response.json()["msg"] == "register success"


@when('I login via api with username "{u}" and password "{p}"')
def step_login_api(context, u, p):
    payload = {"username": u, "password": p}
    context.response = requests.post(
        f"{context.base_url}/api/login",
        json=payload
    )


@then('api login response should be "{msg}"')
def step_login_result(context, msg):
    assert context.response.json()["msg"] == msg


@when("I get user list via api")
def step_get_users(context):
    context.response = requests.get(f"{context.base_url}/api/users")


@then("api user list should not be empty")
def step_users_not_empty(context):
    users = context.response.json()["users"]
    assert len(users) > 0


@when("I create and delete user via api")
def step_create_and_delete(context):
    username = f"del{int(time.time())}"
    payload = {"username": username, "password": "123456"}
    requests.post(f"{context.base_url}/api/register", json=payload)
    context.response = requests.get(f"{context.base_url}/api/delete/{username}")


@then("api delete response should be success")
def step_delete_success(context):
    assert context.response.json()["msg"] == "delete success"