import pytest


@pytest.fixture
def selenium(selenium):
    selenium.implicitly_wait(10)
    selenium.maximize_window()
    return selenium


@pytest.fixture
def chrome_options(chrome_options):
    chrome_options.binary_location = '/usr/bin/chromium-browser'
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-dev-shm-usage')
    return chrome_options
