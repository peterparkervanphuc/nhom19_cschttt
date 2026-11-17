"""Read-only process/resource observations; never substitutes estimates for probes."""

import ctypes
import os
from pathlib import Path
import shutil
import sys


def resource_snapshot(directory: Path) -> dict:
    directory = directory.resolve()
    while not directory.exists():
        directory = directory.parent
    result = {"pid": os.getpid(), "disk_free_bytes": shutil.disk_usage(directory).free,
              "peak_process_rss_bytes": None, "system_available_ram_bytes": None,
              "worker_processes": 0, "device": "cpu", "vram_allocated_bytes": 0,
              "vram_reserved_bytes": 0, "gpu_provider_observation": "not measured; CPU execution"}
    if sys.platform == "win32":
        from ctypes import wintypes

        class MemoryStatus(ctypes.Structure):
            _fields_ = [("length", wintypes.DWORD), ("load", wintypes.DWORD)] + [
                (name, ctypes.c_ulonglong) for name in ("total_physical", "available_physical",
                "total_pagefile", "available_pagefile", "total_virtual", "available_virtual", "extended")]

        class ProcessMemory(ctypes.Structure):
            _fields_ = [("cb", wintypes.DWORD), ("faults", wintypes.DWORD)] + [
                (name, ctypes.c_size_t) for name in ("peak_working_set", "working_set", "peak_paged",
                "paged", "peak_nonpaged", "nonpaged", "pagefile", "peak_pagefile")]

        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        psapi = ctypes.WinDLL("psapi", use_last_error=True)
        kernel.GetCurrentProcess.restype = wintypes.HANDLE
        kernel.GlobalMemoryStatusEx.argtypes = [ctypes.POINTER(MemoryStatus)]
        psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.POINTER(ProcessMemory), wintypes.DWORD]
        memory = MemoryStatus()
        memory.length = ctypes.sizeof(memory)
        process = ProcessMemory()
        process.cb = ctypes.sizeof(process)
        if kernel.GlobalMemoryStatusEx(ctypes.byref(memory)):
            result["system_available_ram_bytes"] = memory.available_physical
            result["system_total_ram_bytes"] = memory.total_physical
        if psapi.GetProcessMemoryInfo(kernel.GetCurrentProcess(), ctypes.byref(process), process.cb):
            result["peak_process_rss_bytes"] = process.peak_working_set
            result["process_rss_bytes"] = process.working_set
    else:
        import resource
        peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        result["peak_process_rss_bytes"] = peak if sys.platform == "darwin" else peak * 1024
    result["peak_scope"] = "process lifetime high-water mark; no worker processes spawned by this runner"
    return result
