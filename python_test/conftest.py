import pytest
import os
import json
import time
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

BASE_URL = os.getenv("APP_BASE_URL", "http://127.0.0.1:5000")
REPORTS_DIR = Path(__file__).parent / "reports"

@pytest.fixture(scope="session")
def base_url(): return BASE_URL

@pytest.fixture(scope="function")
def driver():
    service = Service("/Users/liangchang/code/frameworks_convert/chromedriver/chromedriver")
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(service=service, options=options)
    driver.find = lambda sel: driver.find_element(By.CSS_SELECTOR, sel)
    yield driver
    driver.quit()

_results = []
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call":
        _results.append({"node": item.nodeid, "outcome": rep.outcome, "duration": rep.duration})

def pytest_sessionfinish(session, exitstatus):
    if not _results: return
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(REPORTS_DIR / "pytest_results.json", "w") as f: json.dump(_results, f, indent=2)
