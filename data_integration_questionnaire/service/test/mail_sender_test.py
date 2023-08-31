from data_integration_questionnaire.service.mail_sender import validate_address


def test_validate_address_positive_1():
    assert validate_address("john.doe@gmail.com")


def test_validate_address_positive_2():
    assert validate_address("john.doe@onepointltd.com")


def test_validate_address_negative_1():
    assert not validate_address("john.doegmail.com")
