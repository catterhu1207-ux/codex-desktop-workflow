"""Elapsed execution time that excludes Windows sleep and hibernation."""
import ctypes
import os
import time


def seconds() -> float:
    if os.name != "nt":
        return time.monotonic()
    query = ctypes.WinDLL("kernel32", use_last_error=True).QueryUnbiasedInterruptTime
    query.argtypes = [ctypes.POINTER(ctypes.c_ulonglong)]
    query.restype = ctypes.c_int
    value = ctypes.c_ulonglong()
    if not query(ctypes.byref(value)):
        raise ctypes.WinError(ctypes.get_last_error())
    return value.value / 10_000_000
