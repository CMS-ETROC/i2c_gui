from __future__ import annotations

import re

def hex_0fill(val: str, bits: int):
    from math import ceil
    if type(val) == "<class 'str'>":
        val = int(val, 0)
    return "{0:#0{1}x}".format(val, ceil(bits/4) + 2)  # We have to add 2 to account for the two characters which make the hex identifier, i.e. '0x'

def validate_8bit_register(string: str):
    digit_regex = r"\d{0,3}"
    hex_regex   = r"0x[a-fA-F\d]{0,2}"

    if string == "":
        return True

    if re.fullmatch(digit_regex, string) is not None:
        if int(string, 10) < 256:
            return True

    if re.fullmatch(hex_regex, string) is not None:
        return True

    return False

def validate_variable_bit_register(string: str, bits: int):
    digit_regex = r"\d+"
    hex_regex   = r"0x[a-fA-F\d]*"
    max_val = 2**bits

    if string == "":
        return True

    if re.fullmatch(digit_regex, string) is not None:
        if int(string, 10) < max_val:
            return True

    if re.fullmatch(hex_regex, string) is not None:
        if string == "0x" or int(string, 16) < max_val:
            return True

    return False

def validate_i2c_address(string: str):
    digit_regex = r"\d{0,3}"
    hex_regex   = r"0x[a-fA-F\d]{0,2}"

    if string == "":
        return True

    if re.fullmatch(digit_regex, string) is not None:
        if int(string, 10) <= 127:
            return True

    if re.fullmatch(hex_regex, string) is not None:
        if string == "0x" or int(string, 16) <= 127:
            return True

    return False

def validate_pixel_index(string: str):
    if string == "":
        return True
    digit_regex = r"\d{0,2}"

    if re.fullmatch(digit_regex, string) is not None:
        if int(string, 10) < 16:
            return True

    return False