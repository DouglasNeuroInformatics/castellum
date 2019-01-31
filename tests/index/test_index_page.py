
def test_index_page_has_three_links(selenium):
    selenium.get('http://127.0.0.1:8000/login/')
    selenium.find_element_by_id("id_username").send_keys("admin")
    selenium.find_element_by_id("id_password").send_keys("123")
    selenium.find_element_by_css_selector('input.btn').click()

    element1 = selenium.find_element_by_link_text('Studies').text
    element2 = selenium.find_element_by_link_text('Subjects').text
    element3 = selenium.find_element_by_link_text('Recruitment').text

    assert element1 == 'Studies'
    assert element2 == 'Subjects'
    assert element3 == 'Recruitment'
