import time

BASE_URL = "http://127.0.0.1:5000"


def test_login_success(page):

    page.goto(f"{BASE_URL}/login")

    page.fill("#username", "admin")
    page.fill("#password", "123456")

    page.click("#loginBtn")

    page.wait_for_url("**/dashboard")

    assert "dashboard" in page.url


def test_register_user(page):

    page.goto(f"{BASE_URL}/register")

    username = "user" + str(int(time.time()))

    page.fill("#username", username)
    page.fill("#password", "123456")

    page.click("#registerBtn")

    page.wait_for_url("**/login")

    assert "login" in page.url


def test_delete_user(page):

    page.goto(f"{BASE_URL}/login")

    page.fill("#username", "admin")
    page.fill("#password", "123456")

    page.click("#loginBtn")

    page.wait_for_url("**/dashboard")

    page.goto(f"{BASE_URL}/users")

    page.click("a[href^='/delete/']")

    assert "删除成功" in page.content()


def test_iframe_page(page):

    page.goto(f"{BASE_URL}/iframe")

    # 等待 iframe 出现
    page.wait_for_selector("#myframe")

    # 在 iframe 内查找
    frame = page.frame_locator("#myframe")

    frame.get_by_text("用户列表").wait_for()

    assert frame.get_by_text("用户列表").is_visible()