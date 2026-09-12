import re


def normalize_phone(phone):
    if not phone:
        return None

    phone = str(phone).strip()

    # Persian digits → English digits
    persian_digits = "۰۱۲۳۴۵۶۷۸۹"
    english_digits = "0123456789"

    translation_table = str.maketrans(
        persian_digits,
        english_digits
    )

    phone = phone.translate(translation_table)

    # Remove spaces, -, (, ), etc.
    phone = re.sub(r"\D", "", phone)

    # +98 / 98 / 0098 → 0
    if phone.startswith("0098"):
        phone = "0" + phone[4:]

    elif phone.startswith("98"):
        phone = "0" + phone[2:]

    # Validate Iranian mobile
    if re.fullmatch(r"09\d{9}", phone):
        return phone

    return None