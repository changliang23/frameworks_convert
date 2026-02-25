from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

# ====== 简化 find 以符合转换规范 ======
class SimpleDriver(webdriver.Chrome):
    def __init__(self):
        service = Service("/Users/liangchang/code/frameworks_convert/chromedriver/chromedriver")
        super().__init__(service=service)

    def find(self, selector):
        return self.find_element(By.CSS_SELECTOR, selector)

def test_login_success():
    driver = SimpleDriver()
    driver.get("http://127.0.0.1:5000/login")

    driver.find("#username").send_keys("admin")
    driver.find("#password").send_keys("123456")
    driver.find("#loginBtn").click()

    assert "首页" in driver.page_source

    driver.quit()


def test_login_fail():
    driver = SimpleDriver()
    driver.get("http://127.0.0.1:5000/login")

    driver.find("#username").send_keys("admin")
    driver.find("#password").send_keys("wrong")
    driver.find("#loginBtn").click()

    assert "登录失败" in driver.page_source

    driver.quit()


def test_register_user():
    driver = SimpleDriver()
    driver.get("http://127.0.0.1:5000/register")

    driver.find("#username").send_keys("testuser")
    driver.find("#password").send_keys("111111")
    driver.find("#registerBtn").click()

    assert "登录" in driver.page_source

    driver.quit()


def test_delete_user():
    driver = SimpleDriver()
    driver.get("http://127.0.0.1:5000/login")

    driver.find("#username").send_keys("admin")
    driver.find("#password").send_keys("123456")
    driver.find("#loginBtn").click()

    driver.find("a[href='/users']").click()
    driver.find("a[href='/delete/testuser']").click()

    assert "删除成功" in driver.page_source

    driver.quit()


def test_iframe_users_page():
    driver = SimpleDriver()
    driver.get("http://127.0.0.1:5000/iframe")

    iframe = driver.find("#myframe")
    driver.switch_to.frame(iframe)

    assert "用户列表" in driver.page_source

    driver.quit()


def test_upload_file():
    driver = SimpleDriver()
    driver.get("http://127.0.0.1:5000/upload")

    driver.find("#fileInput").send_keys("/path/to/test.txt")
    driver.find("#uploadBtn").click()

    assert "上传成功" in driver.page_source

    driver.quit()
