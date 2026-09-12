import ctypes
import sys


def enable_high_dpi_rendering():
    if sys.platform != "win32":
        return

    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except (AttributeError, OSError):
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except (AttributeError, OSError):
            pass


enable_high_dpi_rendering()

from desktop_app import main


if __name__ == "__main__":
    main()
