import requests

BASE_URL = "http://127.0.0.1:5000"

def login(session):
    r = session.post(
        f"{BASE_URL}/api/login",
        json={"username": "admin", "password": "123456"}
    )
    assert r.status_code == 200

def test_api_register_user():
    s = requests.Session()
    login(s)

    username = f"user{int(__import__('time').time())}"
    resp = requests.post(
        f"{BASE_URL}/api/register",
        json={"username": username, "password": "123456"}
    )
    assert resp.status_code == 200
    assert resp.json()["msg"] == "register success"


def test_api_login_success():
    s = requests.Session()
    login(s)

    resp = requests.post(
        f"{BASE_URL}/api/login",
        json={"username": "admin", "password": "123456"}
    )
    assert resp.status_code == 200
    assert resp.json()["msg"] == "login success"


def test_api_login_fail():
    s = requests.Session()
    login(s)

    resp = requests.post(
        f"{BASE_URL}/api/login",
        json={"username": "admin", "password": "wrong"}
    )
    assert resp.status_code == 401
    assert resp.json()["msg"] == "login failed"


def test_api_get_users():
    s = requests.Session()
    login(s)

    resp = requests.get(f"{BASE_URL}/api/users")
    assert resp.status_code == 200
    assert "users" in resp.json()
    assert isinstance(resp.json()["users"], list)


def test_api_delete_user():
    s = requests.Session()
    login(s)

    # 先创建一个用户
    username = f"deluser{int(__import__('time').time())}"
    requests.post(
        f"{BASE_URL}/api/register",
        json={"username": username, "password": "123456"}
    )

    # 再删除该用户
    resp = requests.get(f"{BASE_URL}/api/delete/{username}")
    assert resp.status_code == 200
    assert resp.json()["msg"] == "delete success"