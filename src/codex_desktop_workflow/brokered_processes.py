"""Read Windows-brokered elevation users of an exact isolated executable.

Restart Manager observes consent requests created outside the caller's Job.
It never approves, closes or terminates a dialog or the Appinfo service.
"""
import ctypes,os
from ctypes import wintypes
from pathlib import Path
import uuid

def pending_elevations(app):
    if os.name!='nt':raise RuntimeError('broker_inspection_requires_windows')
    file=(Path(app)/'resources/codex-windows-sandbox-setup.exe').resolve()
    if not file.is_file() or file.is_symlink():raise RuntimeError('exact_sandbox_setup_resource_missing')
    class UniqueProcess(ctypes.Structure):
        _fields_=[('pid',wintypes.DWORD),('started',wintypes.FILETIME)]
    class Info(ctypes.Structure):
        _fields_=[('process',UniqueProcess),('app_name',wintypes.WCHAR*256),('service',wintypes.WCHAR*64),('app_type',wintypes.UINT),('status',wintypes.ULONG),('session',wintypes.DWORD),('restartable',wintypes.BOOL)]
    api=ctypes.WinDLL('rstrtmgr',use_last_error=True)
    api.RmStartSession.argtypes=[ctypes.POINTER(wintypes.DWORD),wintypes.DWORD,wintypes.LPWSTR]
    api.RmRegisterResources.argtypes=[wintypes.DWORD,wintypes.UINT,ctypes.POINTER(wintypes.LPCWSTR),wintypes.UINT,ctypes.c_void_p,wintypes.UINT,ctypes.c_void_p]
    api.RmGetList.argtypes=[wintypes.DWORD,ctypes.POINTER(wintypes.UINT),ctypes.POINTER(wintypes.UINT),ctypes.POINTER(Info),ctypes.POINTER(wintypes.DWORD)]
    api.RmEndSession.argtypes=[wintypes.DWORD]
    session=wintypes.DWORD();key=ctypes.create_unicode_buffer(uuid.uuid4().hex)
    status=api.RmStartSession(ctypes.byref(session),0,key)
    if status:raise OSError(status,'broker_session_failed')
    try:
        resources=(wintypes.LPCWSTR*1)(str(file))
        status=api.RmRegisterResources(session,1,resources,0,None,0,None)
        if status:raise OSError(status,'broker_resource_registration_failed')
        needed=wintypes.UINT();count=wintypes.UINT();reasons=wintypes.DWORD()
        status=api.RmGetList(session,ctypes.byref(needed),ctypes.byref(count),None,ctypes.byref(reasons))
        if status not in (0,234):raise OSError(status,'broker_query_failed')
        if needed.value>1024:raise RuntimeError('broker_query_bounds')
        rows=(Info*needed.value)();count.value=needed.value
        if needed.value:
            status=api.RmGetList(session,ctypes.byref(needed),ctypes.byref(count),rows,ctypes.byref(reasons))
            if status:raise OSError(status,'broker_query_changed')
        consents=[{'pid':row.process.pid,'created_filetime':row.process.started.dwLowDateTime+(row.process.started.dwHighDateTime<<32),'application':row.app_name} for row in rows[:count.value] if row.app_name.casefold()=='consent.exe' and not row.service]
        return {'status':'none_for_owned_candidate' if not consents else 'pending_elevation_for_owned_candidate','resource':str(file),'requests':consents,'inspection':'restart_manager_exact_resource','processes_terminated':False}
    finally:api.RmEndSession(session)
