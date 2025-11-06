import platform


def detect_os_family() -> str:
    sys = platform.system().lower()
    if "windows" in sys:
        return "windows"
    if "darwin" in sys or "mac" in sys:
        return "mac"
    if "linux" in sys:
        return "linux"
    return sys or "unknown"


def is_windows(family: str | None) -> bool:
    return (family or detect_os_family()) == "windows"


def is_mac(family: str | None) -> bool:
    return (family or detect_os_family()) == "mac"


def is_linux(family: str | None) -> bool:
    return (family or detect_os_family()) == "linux"


