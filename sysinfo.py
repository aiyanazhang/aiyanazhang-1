#!/usr/bin/env python3
"""
System Information Utility
A cross-platform script to display system information including OS, CPU, memory, disk, and uptime.
Supports macOS (Darwin) and Linux.
"""

import platform
import socket
import subprocess
import os
from datetime import datetime


def get_size(bytes):
    """
    Convert bytes to human-readable format (B, KB, MB, GB, TB).
    
    Args:
        bytes: Size in bytes to convert
    
    Returns:
        Formatted string with appropriate unit (e.g., "1.50 GB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes < 1024.0:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024.0


def get_memory_info():
    """
    Retrieve memory information based on the operating system.
    
    For macOS: Uses vm_stat command to get memory page statistics
    For Linux: Reads from /proc/meminfo
    
    Returns:
        tuple: (total, available, used) memory in bytes, or (None, None, None) if unsupported
    """
    system = platform.system()
    if system == "Darwin":
        # Execute vm_stat to get virtual memory statistics on macOS
        vm_stat = subprocess.check_output(['vm_stat']).decode('utf-8')
        lines = vm_stat.split('\n')
        # First line contains page size info
        page_size = int(lines[0].split()[-2])
        
        # Parse memory statistics from vm_stat output
        stats = {}
        for line in lines[1:]:
            if ':' in line:
                key, value = line.split(':')
                stats[key.strip()] = int(value.strip().rstrip('.'))
        
        # Calculate memory values from page counts
        free = stats.get('Pages free', 0) * page_size
        active = stats.get('Pages active', 0) * page_size
        inactive = stats.get('Pages inactive', 0) * page_size
        wired = stats.get('Pages wired down', 0) * page_size
        
        # Get total physical memory using system configuration
        total = os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES')
        used = active + wired
        available = free + inactive
        
        return total, available, used
    elif system == "Linux":
        # Read memory info from /proc/meminfo on Linux
        with open('/proc/meminfo', 'r') as f:
            lines = f.readlines()
            mem_info = {}
            for line in lines:
                key, value = line.split(':')
                # Convert from KB to bytes (meminfo values are in KB)
                mem_info[key.strip()] = int(value.strip().split()[0]) * 1024
            
            total = mem_info['MemTotal']
            available = mem_info['MemAvailable']
            used = total - available
            return total, available, used
    return None, None, None


def get_cpu_count():
    """
    Get the number of physical and logical CPU cores.
    
    For macOS: Uses sysctl command
    For Linux: Uses os.cpu_count() and lscpu
    
    Returns:
        tuple: (physical_cores, logical_cores), or (None, None) if unsupported
    """
    system = platform.system()
    if system == "Darwin":
        # Query CPU info via sysctl on macOS
        physical = int(subprocess.check_output(['sysctl', '-n', 'hw.physicalcpu']).decode().strip())
        logical = int(subprocess.check_output(['sysctl', '-n', 'hw.logicalcpu']).decode().strip())
        return physical, logical
    elif system == "Linux":
        # Get logical CPU count from Python's os module
        logical = os.cpu_count()
        try:
            # Parse physical core count from lscpu output
            physical = int(subprocess.check_output("lscpu | grep 'Core(s) per socket' | awk '{print $4}'", shell=True).decode().strip())
        except:
            # Fallback to logical count if parsing fails
            physical = logical
        return physical, logical
    return None, None


def get_uptime():
    """
    Get the system boot time.
    
    For macOS: Uses sysctl kern.boottime
    For Linux: Reads from /proc/uptime
    
    Returns:
        datetime: Boot time as a datetime object, or None if unsupported
    """
    system = platform.system()
    if system == "Darwin":
        # Get boot time from kernel on macOS
        uptime = subprocess.check_output(['sysctl', '-n', 'kern.boottime']).decode()
        # Parse the boot timestamp from sysctl output
        boot_time = int(uptime.split()[3].rstrip(','))
        return datetime.fromtimestamp(boot_time)
    elif system == "Linux":
        # Read uptime in seconds from /proc/uptime on Linux
        with open('/proc/uptime', 'r') as f:
            uptime_seconds = float(f.readline().split()[0])
            # Calculate boot time by subtracting uptime from current time
            boot_time = datetime.now().timestamp() - uptime_seconds
            return datetime.fromtimestamp(boot_time)
    return None


def display_system_info():
    """
    Display comprehensive system information including:
    - Operating System details
    - Kernel information
    - Hostname
    - CPU core counts
    - Memory usage
    - Disk space
    - System boot time
    """
    # Header
    print("=" * 60)
    print("System Information".center(60))
    print("=" * 60)
    
    # Operating System Information
    print("\n[Operating System]")
    print(f"OS: {platform.system()}")
    print(f"Version: {platform.version()}")
    print(f"Release: {platform.release()}")
    print(f"Architecture: {platform.machine()}")
    print(f"Processor: {platform.processor()}")
    
    # Kernel Information
    print("\n[Kernel]")
    uname = platform.uname()
    print(f"Kernel: {uname.system} {uname.release}")
    
    # Network Hostname
    print("\n[Hostname]")
    print(f"Hostname: {socket.gethostname()}")
    
    # CPU Information
    print("\n[CPU]")
    physical, logical = get_cpu_count()
    if physical and logical:
        print(f"Physical cores: {physical}")
        print(f"Logical cores: {logical}")
    
    # Memory Information
    print("\n[Memory]")
    total, available, used = get_memory_info()
    if total and available and used:
        used_percent = (used / total) * 100
        print(f"Total: {get_size(total)}")
        print(f"Available: {get_size(available)}")
        print(f"Used: {get_size(used)} ({used_percent:.1f}%)")
    
    # Disk Information
    print("\n[Disk]")
    system = platform.system()
    if system == "Darwin":
        # Use df command on macOS
        df_output = subprocess.check_output(['df', '-h']).decode('utf-8')
        print(df_output)
    elif system == "Linux":
        # Use df command with total on Linux
        df_output = subprocess.check_output(['df', '-h', '--total']).decode('utf-8')
        print(df_output)
    
    # Boot Time Information
    print("\n[Boot Time]")
    boot_time = get_uptime()
    if boot_time:
        print(f"Boot Time: {boot_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Footer
    print("=" * 60)


# Entry point - run the display function when script is executed directly
if __name__ == "__main__":
    display_system_info()
