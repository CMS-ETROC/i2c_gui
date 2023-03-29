#############################################################################
# zlib License
#
# (C) 2023 Cristóvão Beirão da Cruz e Silva <cbeiraod@cern.ch>
#
# This software is provided 'as-is', without any express or implied
# warranty.  In no event will the authors be held liable for any damages
# arising from the use of this software.
#
# Permission is granted to anyone to use this software for any purpose,
# including commercial applications, and to alter it and redistribute it
# freely, subject to the following restrictions:
#
# 1. The origin of this software must not be misrepresented; you must not
#    claim that you wrote the original software. If you use this software
#    in a product, an acknowledgment in the product documentation would be
#    appreciated but is not required.
# 2. Altered source versions must be plainly marked as such, and must not be
#    misrepresented as being the original software.
# 3. This notice may not be removed or altered from any source distribution.
#############################################################################
# Except portions clearly stated as having been taken from another source

from __future__ import annotations

import re
import logging

# Function from: https://stackoverflow.com/a/35804945
def addLoggingLevel(levelName, levelNum, methodName=None):
    """
    Comprehensively adds a new logging level to the `logging` module and the
    currently configured logging class.

    `levelName` becomes an attribute of the `logging` module with the value
    `levelNum`. `methodName` becomes a convenience method for both `logging`
    itself and the class returned by `logging.getLoggerClass()` (usually just
    `logging.Logger`). If `methodName` is not specified, `levelName.lower()` is
    used.

    To avoid accidental clobberings of existing attributes, this method will
    raise an `AttributeError` if the level name is already an attribute of the
    `logging` module or if the method name is already present

    Example
    -------
    >>> addLoggingLevel('TRACE', logging.DEBUG - 5)
    >>> logging.getLogger(__name__).setLevel("TRACE")
    >>> logging.getLogger(__name__).trace('that worked')
    >>> logging.trace('so did this')
    >>> logging.TRACE
    5
    """
    if not methodName:
        methodName = levelName.lower()

    if hasattr(logging, levelName):
       raise AttributeError('{} already defined in logging module'.format(levelName))
    if hasattr(logging, methodName):
       raise AttributeError('{} already defined in logging module'.format(methodName))
    if hasattr(logging.getLoggerClass(), methodName):
       raise AttributeError('{} already defined in logger class'.format(methodName))

    # This method was inspired by the answers to Stack Overflow post
    # http://stackoverflow.com/q/2183233/2988730, especially
    # http://stackoverflow.com/a/13638084/2988730
    def logForLevel(self, message, *args, **kwargs):
        if self.isEnabledFor(levelNum):
            self._log(levelNum, message, args, **kwargs)
    def logToRoot(message, *args, **kwargs):
        logging.log(levelNum, message, *args, **kwargs)

    logging.addLevelName(levelNum, levelName)
    setattr(logging, levelName, levelNum)
    setattr(logging.getLoggerClass(), methodName, logForLevel)
    setattr(logging, methodName, logToRoot)

def hex_0fill(val: str, bits: int):
    from math import ceil
    if type(val) == str:
        if val == '':
            val = 0
        else:
            val = int(val, 0)
    return "{0:#0{1}x}".format(val, ceil(bits/4) + 2)  # We have to add 2 to account for the two characters which make the hex identifier, i.e. '0x'

def validate_num(string: str):
    digit_regex = r"\d+"

    if string == "":
        return True

    if re.fullmatch(digit_regex, string) is not None:
        return True

    return False

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