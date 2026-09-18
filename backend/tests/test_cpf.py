from app.cpf import is_valid_cpf, mask_cpf


def test_valid_cpf():
    assert is_valid_cpf("111.444.777-35")


def test_invalid_cpf_checksum():
    assert not is_valid_cpf("111.444.777-36")


def test_invalid_cpf_all_same_digits():
    assert not is_valid_cpf("111.111.111-11")


def test_invalid_cpf_wrong_length():
    assert not is_valid_cpf("123")


def test_mask_cpf():
    assert mask_cpf("11144477735") == "***.***.777-35"
