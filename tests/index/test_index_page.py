import pytest

def test_open_main_page(selenium):
    selenium.get('http://127.0.0.1:8000/login/')
    selenium.find_element_by_id("id_username").send_keys("admin")
    selenium.find_element_by_id("id_password").send_keys("123")
    selenium.driver.find_element_by_css_selector('input.btn').click()
