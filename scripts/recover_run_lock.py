"""Inspect or remove a stale writer.lock left by a local Windows run."""

import argparse
from contextlib import contextmanager
import ctypes
from ctypes import wintypes
import os
from pathlib import Path
import stat
import sys


GENERIC_READ = 0x80000000
DELETE = 0x00010000
SHARE_ALL = 0x7  # Read, write, and delete sharing for inspection.
OPEN_EXISTING = 3
OPEN_REPARSE_POINT = 0x00200000
FILE_DISPOSITION_INFO = 4
SYNCHRONIZE = 0x00100000
ERROR_INVALID_PARAMETER = 87
DRIVE_REMOTE = 4
WAIT_OBJECT_0 = 0
WAIT_TIMEOUT = 258
INVALID_HANDLE = ctypes.c_void_p(-1).value


def windows_api():
    api = ctypes.WinDLL("kernel32", use_last_error=True)
    api.CreateFileW.argtypes = (
        wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, wintypes.LPVOID,
        wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE,
    )
    api.CreateFileW.restype = wintypes.HANDLE
    api.OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
    api.OpenProcess.restype = wintypes.HANDLE
    api.WaitForSingleObject.argtypes = (wintypes.HANDLE, wintypes.DWORD)
    api.WaitForSingleObject.restype = wintypes.DWORD
    api.CloseHandle.argtypes = (wintypes.HANDLE,)
    api.CloseHandle.restype = wintypes.BOOL
    api.GetDriveTypeW.argtypes = (wintypes.LPCWSTR,)
    api.GetDriveTypeW.restype = wintypes.UINT
    api.SetFileInformationByHandle.argtypes = (
        wintypes.HANDLE, ctypes.c_int, wintypes.LPVOID, wintypes.DWORD,
    )
    api.SetFileInformationByHandle.restype = wintypes.BOOL
    return api


@contextmanager
def open_marker(api, path: Path, *, for_removal: bool):
    import msvcrt

    access = GENERIC_READ | DELETE if for_removal else GENERIC_READ
    sharing = 0 if for_removal else SHARE_ALL
    handle = api.CreateFileW(str(path), access, sharing, None, OPEN_EXISTING,
                             OPEN_REPARSE_POINT, None)
    if handle == INVALID_HANDLE:
        error = ctypes.get_last_error()
        if error == 2:
            yield None
            return
        raise ctypes.WinError(error)
    try:
        descriptor = msvcrt.open_osfhandle(handle, os.O_RDONLY | os.O_BINARY)
    except OSError:
        api.CloseHandle(handle)
        raise
    try:
        info = os.fstat(descriptor)
        if not stat.S_ISREG(info.st_mode) or info.st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT:
            raise ValueError("writer.lock must be a regular file")
        raw_pid = os.read(descriptor, 11)
        if len(raw_pid) > 10 or not raw_pid.isdigit() or not 0 < int(raw_pid) <= 0xFFFFFFFF:
            raise ValueError("writer.lock does not contain a valid PID")
        yield handle, int(raw_pid)
    finally:
        os.close(descriptor)


def process_has_exited(api, pid: int) -> bool:
    handle = api.OpenProcess(SYNCHRONIZE, False, pid)
    if not handle:
        error = ctypes.get_last_error()
        if error == ERROR_INVALID_PARAMETER:
            return True  # There is no process with this PID.
        raise ctypes.WinError(error)
    try:
        status = api.WaitForSingleObject(handle, 0)
        if status == WAIT_OBJECT_0:
            return True
        if status == WAIT_TIMEOUT:
            return False
        raise ctypes.WinError(ctypes.get_last_error())
    finally:
        api.CloseHandle(handle)


def recover_run_lock(directory: Path, *, remove: bool = False) -> str:
    if sys.platform != "win32":
        raise ValueError("This recovery tool requires a local Windows run")
    directory = directory.resolve(strict=True)
    if not directory.is_dir():
        raise ValueError("Run directory must be a directory")
    path = directory / "writer.lock"
    api = windows_api()
    if api.GetDriveTypeW(directory.anchor) == DRIVE_REMOTE:
        raise ValueError("Run directory must be on a local drive to verify its process owner")
    with open_marker(api, path, for_removal=False) as marker:
        if marker is None:
            return "missing"
        _, pid = marker
        if not process_has_exited(api, pid):
            return "active"
    if not remove:
        return "stale"

    # Recheck the PID under the exclusive handle. Mark that exact file for
    # deletion before closing it so a new writer's marker cannot be removed.
    with open_marker(api, path, for_removal=True) as marker:
        if marker is None:
            return "missing"
        handle, current_pid = marker
        if current_pid != pid or not process_has_exited(api, current_pid):
            return "changed"
        delete_on_close = wintypes.BOOLEAN(True)
        if not api.SetFileInformationByHandle(handle, FILE_DISPOSITION_INFO,
                                              ctypes.byref(delete_on_close), ctypes.sizeof(delete_on_close)):
            raise ctypes.WinError(ctypes.get_last_error())
    return "removed"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog="After removing a stale marker, rerun the original command with the same output directory.",
    )
    parser.add_argument("directory", type=Path, help="Directory containing the run's writer.lock")
    parser.add_argument("--remove", action="store_true", help="Remove the marker if its owner has exited")
    args = parser.parse_args(argv)
    try:
        status = recover_run_lock(args.directory, remove=args.remove)
    except (OSError, ValueError) as error:
        print(f"Recovery failed: {error}", file=sys.stderr)
        return 1
    print(f"writer.lock: {status}")
    return int(args.remove and status in {"active", "changed"})


if __name__ == "__main__":
    raise SystemExit(main())
