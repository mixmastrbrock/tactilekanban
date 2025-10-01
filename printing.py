"""
Helper functions for interfacing with the thermal receipt printer using python‑escpos.

This module initializes a singleton printer object using the environment
variables defined in the main application.  The `print_task` function
formats and prints task information, and `ensure_printer_ready` ensures
that the printer is connected before the first print attempt.

If you need to support network, serial or Bluetooth connections instead of
USB, adjust the initialization accordingly (e.g. using `escpos.printer.Network`).
"""

import os
from datetime import datetime
from typing import Optional

from escpos.printer import Usb

_printer: Optional[Usb] = None


def _init_printer() -> Usb:
    """Instantiate and return a Usb printer based on environment variables.

    Raises
    ------
    ValueError
        If required environment variables are missing or invalid.
    """
    vendor_hex = os.environ.get("PRINTER_VENDOR_ID")
    product_hex = os.environ.get("PRINTER_PRODUCT_ID")
    if not vendor_hex or not product_hex:
        raise ValueError("PRINTER_VENDOR_ID and PRINTER_PRODUCT_ID must be set")

    try:
        vid = int(vendor_hex, 16)
        pid = int(product_hex, 16)
    except ValueError as exc:
        raise ValueError("Vendor and product IDs must be valid hexadecimal strings") from exc

    interface = int(os.environ.get("PRINTER_INTERFACE", 0))
    profile = os.environ.get("PRINTER_PROFILE", None)
    # Create the Usb printer object
    return Usb(vid, pid, interface, profile=profile)


def ensure_printer_ready() -> None:
    """Initialize the global printer instance if not already initialized.

    This function should be called on application startup to fail fast if
    the printer is not reachable.  Subsequent calls do nothing.
    """
    global _printer  # noqa: PLW0603
    if _printer is None:
        _printer = _init_printer()


def print_task(title: str, description: str, created: datetime, due: datetime) -> None:
    """Send a task to the thermal printer.

    Parameters
    ----------
    title : str
        The title of the task.
    description : str
        The task description.
    created : datetime
        Datetime when the task was created.
    due : datetime
        Datetime when the task is due.

    Raises
    ------
    RuntimeError
        If the printer is not initialized.
    """
    global _printer  # noqa: PLW0603
    if _printer is None:
        _printer = _init_printer()

    # Ensure Unicode strings are passed to the printer.  The python‑escpos
    # library will encode them using the MagicEncode mechanism【236721273609996†L1038-L1053】.
    task_lines = [
        title,
        description,
        f"Created: {created:%Y-%m-%d %H:%M}",
        f"Due:     {due:%Y-%m-%d %H:%M}",
    ]

    # Set some styles: bold for title, normal for the rest
    _printer.set(align="left", text_type="b")
    _printer.textln(task_lines[0] + "\n")
    _printer.set(text_type="normal")
    for line in task_lines[1:]:
        _printer.textln(line + "\n")
    _printer.cut()