def test_str(address):
    assert "10787 Berlin, Hardenbergplatz 8" == str(address)


def test_str_with_additional_information(address):
    address.additional_information = "appartment 3"
    assert "10787 Berlin, Hardenbergplatz 8 appartment 3" == str(address)
