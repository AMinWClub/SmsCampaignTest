from validators.phone_normalizer import normalize_phone


def test_normalize_persian_digits():
    assert normalize_phone("۰۹۱۲۳۴۵۶۷۸۹") == "09123456789"


def test_normalize_98_prefix():
    assert normalize_phone("989123456789") == "09123456789"


def test_normalize_0098_prefix():
    assert normalize_phone("00989123456789") == "09123456789"


def test_normalize_phone_with_spaces_and_symbols():
    assert normalize_phone("0912-345-6789") == "09123456789"


def test_invalid_phone_is_removed():
    assert normalize_phone("09123") is None


def test_invalid_phone_text_is_removed():
    assert normalize_phone("hello") is None


def test_empty_phone_is_removed():
    assert normalize_phone("") is None


def test_none_phone_is_removed():
    assert normalize_phone(None) is None
