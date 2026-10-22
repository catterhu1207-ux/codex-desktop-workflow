"""Read Windows integrity labels before native desktop launch; never change them."""
import ctypes
from ctypes import wintypes
import os

MEDIUM = 8192


def require_desktop_integrity(file_level, process_level):
    if process_level < MEDIUM:
        raise RuntimeError('native_desktop_host_low_integrity: current process cannot create the required isolated desktop')
    if file_level < MEDIUM:
        raise RuntimeError('native_desktop_executable_low_integrity: candidate location marks the executable for low-integrity execution; use the designated application build directory with its existing security settings')
    return {'status': 'passed', 'file_integrity': file_level,
            'host_integrity': process_level, 'security_settings_modified': False}


def _libraries():
    if os.name != 'nt':
        raise RuntimeError('native_desktop_integrity_requires_windows')
    adv = ctypes.WinDLL('advapi32', use_last_error=True)
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    adv.GetNamedSecurityInfoW.argtypes = [wintypes.LPWSTR, wintypes.DWORD, wintypes.DWORD,
        ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p,
        ctypes.POINTER(ctypes.c_void_p), ctypes.POINTER(ctypes.c_void_p)]
    adv.GetNamedSecurityInfoW.restype = wintypes.DWORD
    adv.GetAce.argtypes = [ctypes.c_void_p, wintypes.DWORD, ctypes.POINTER(ctypes.c_void_p)]
    adv.GetAce.restype = wintypes.BOOL
    kernel.LocalFree.argtypes = [ctypes.c_void_p]
    kernel.LocalFree.restype = ctypes.c_void_p
    kernel.GetCurrentProcess.restype = wintypes.HANDLE
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    adv.OpenProcessToken.argtypes = [wintypes.HANDLE, wintypes.DWORD, ctypes.POINTER(wintypes.HANDLE)]
    adv.GetTokenInformation.argtypes = [wintypes.HANDLE, wintypes.DWORD, ctypes.c_void_p,
        wintypes.DWORD, ctypes.POINTER(wintypes.DWORD)]
    return adv, kernel


def _sid_level(address):
    header = ctypes.string_at(address, 8)
    if header[0] != 1 or header[1] != 1 or header[2:] != b'\0\0\0\0\0\x10':
        raise RuntimeError('native_desktop_integrity_sid_invalid')
    return int.from_bytes(ctypes.string_at(address + 8, 4), 'little')


def executable_integrity(path):
    adv, kernel = _libraries()
    sacl, descriptor = ctypes.c_void_p(), ctypes.c_void_p()
    error = adv.GetNamedSecurityInfoW(str(path), 1, 0x10, None, None, None,
                                    ctypes.byref(sacl), ctypes.byref(descriptor))
    if error:
        raise RuntimeError('native_desktop_integrity_label_unreadable:' + str(error))
    try:
        levels = []
        if sacl:
            count = int.from_bytes(ctypes.string_at(sacl.value + 4, 2), 'little')
            for index in range(count):
                ace = ctypes.c_void_p()
                if not adv.GetAce(sacl, index, ctypes.byref(ace)):
                    raise ctypes.WinError(ctypes.get_last_error())
                if ctypes.c_ubyte.from_address(ace.value).value == 17:
                    levels.append(_sid_level(ace.value + 8))
        if len(levels) > 1:
            raise RuntimeError('native_desktop_integrity_label_ambiguous')
        return levels[0] if levels else MEDIUM
    finally:
        if descriptor:
            kernel.LocalFree(descriptor)


def process_integrity(process=None):
    adv, kernel = _libraries()
    token = wintypes.HANDLE()
    if not adv.OpenProcessToken(process or kernel.GetCurrentProcess(), 8, ctypes.byref(token)):
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        needed = wintypes.DWORD()
        adv.GetTokenInformation(token, 25, None, 0, ctypes.byref(needed))
        buffer = ctypes.create_string_buffer(needed.value)
        if not adv.GetTokenInformation(token, 25, buffer, needed, ctypes.byref(needed)):
            raise ctypes.WinError(ctypes.get_last_error())
        return _sid_level(ctypes.c_void_p.from_buffer(buffer).value)
    finally:
        kernel.CloseHandle(token)


def check_native_desktop(executable):
    return require_desktop_integrity(executable_integrity(executable), process_integrity())
