"""
Main entry point for the thermal receipt printer web application.

This app exposes both a simple HTML form and a JSON‑based API for printing
task information to an ESC/POS thermal printer.  It relies on the
python‑escpos library to communicate with the printer and FastAPI to
provide the web interface.

Environment variables
---------------------

PRINTER_VENDOR_ID (required)
    USB vendor ID for the thermal printer, specified in hexadecimal (e.g. "0x0416").

PRINTER_PRODUCT_ID (required)
    USB product ID for the thermal printer, specified in hexadecimal (e.g. "0x5011").

PRINTER_INTERFACE (optional)
    USB interface number, default is 0.

PRINTER_PROFILE (optional)
    Name of the printer profile from the python‑escpos profiles database.  This
    helps the library choose the correct code pages and capabilities for your
    printer.  If omitted, the generic profile is used.

Note: If your printer is accessible via network, serial or Bluetooth, you can
adapt the `printing.py` module accordingly.  This file assumes USB.
"""

import os
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, validator
from starlette.templating import Jinja2Templates

from printing import print_task, ensure_printer_ready


app = FastAPI(title="Task Printer", description="Print tasks to a thermal receipt printer")

BASE_DIR = Path(__file__).resolve().parent

# Mount static files for service worker and manifest
static_dir = BASE_DIR / "static"
templates_dir = BASE_DIR / "templates"
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Configure Jinja2 templates
templates = Jinja2Templates(directory=templates_dir)


class PrintRequest(BaseModel):
    """Pydantic model for JSON API requests."""

    title: str
    description: str
    created_on: datetime
    due_by: datetime

    @validator("title", "description")
    def not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Field cannot be empty")
        return v


# Ensure the printer is initialized when the application starts
ensure_printer_ready()


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    """Serve the HTML form for printing."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/print", response_class=HTMLResponse)
async def print_from_form(
    request: Request,
    title: str = Form(...),
    description: str = Form(...),
    created_on: str = Form(...),
    due_by: str = Form(...),
) -> HTMLResponse:
    """Process form submission and send data to the printer.

    The date/time fields are expected in the browser's `datetime-local` format.
    """
    try:
        created = datetime.fromisoformat(created_on)
        due = datetime.fromisoformat(due_by)
    except ValueError:
        return HTMLResponse(content="Invalid date/time format", status_code=400)

    # Print the task
    try:
        print_task(title, description, created, due)
    except Exception as exc:  # noqa: BLE001
        # Return a simple error page; in a real application you might log this
        return HTMLResponse(content=f"Error printing: {exc}", status_code=500)

    # Display a confirmation page
    return templates.TemplateResponse(
        "confirmation.html",
        {
            "request": request,
            "title": title,
            "description": description,
            "created_on": created,
            "due_by": due,
        },
    )


@app.post("/api/print", response_class=JSONResponse)
async def print_via_api(payload: PrintRequest) -> JSONResponse:
    """API endpoint for printing via JSON.

    Accepts a JSON body with title, description, created_on and due_by fields.
    Returns a JSON response indicating success or failure.
    """
    try:
        print_task(payload.title, payload.description, payload.created_on, payload.due_by)
    except Exception as exc:  # noqa: BLE001
        return JSONResponse(status_code=500, content={"status": "error", "detail": str(exc)})
    return JSONResponse(content={"status": "success"})