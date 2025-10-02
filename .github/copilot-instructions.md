# GitHub Copilot Instructions for tactilekanban

## Project Overview

This is a FastAPI-based web application that prints task information to ESC/POS thermal receipt printers. The application provides both a web form interface and a JSON API for printing task cards to create a physical kanban board.

## Technology Stack

- **Framework**: FastAPI (Python 3.11+)
- **Printer Library**: python-escpos
- **Template Engine**: Jinja2
- **Server**: Uvicorn
- **Deployment**: Docker container

## Project Structure

- `main.py` - Main FastAPI application with web form and API endpoints
- `printing.py` - Printer interface module with USB printer initialization
- `templates/` - Jinja2 HTML templates (index.html, confirmation.html)
- `static/` - Static files including PWA service worker and manifest
- `Dockerfile` - Container build instructions
- `requirements.txt` - Python dependencies

## Environment Variables

The application requires the following environment variables:

- `PRINTER_VENDOR_ID` (required) - USB vendor ID in hexadecimal (e.g., "0x0416")
- `PRINTER_PRODUCT_ID` (required) - USB product ID in hexadecimal (e.g., "0x5011")
- `PRINTER_INTERFACE` (optional) - USB interface number (default: 0)
- `PRINTER_PROFILE` (optional) - Printer profile name from python-escpos database

## Code Style and Standards

- Use type hints for all function parameters and return values
- Follow PEP 8 style guidelines
- Use docstrings for all functions and classes (NumPy/Google style preferred)
- Keep imports organized: standard library, third-party, local modules
- Use meaningful variable names
- Handle exceptions appropriately with specific error messages

## Key Implementation Details

### Printer Initialization

- The printer is initialized as a singleton in `printing.py`
- Initialization happens at application startup via `ensure_printer_ready()`
- USB connection is used by default; can be adapted for network/serial/Bluetooth

### API Endpoints

- `GET /` - Serves the HTML form for printing tasks
- `POST /print` - Processes form submissions and prints tasks (returns HTML)
- `POST /api/print` - JSON API endpoint for printing tasks (returns JSON)

### Date/Time Handling

- Form inputs use ISO format from `datetime-local` HTML input type
- API expects datetime objects in ISO format
- Dates are formatted as `YYYY-MM-DD HH:MM` on printed receipts

### PWA Features

- Service worker (`static/sw.js`) provides offline-first caching
- Manifest file enables installation as a Progressive Web App
- Core application shell is cached for offline access

## Development Workflow

### Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export PRINTER_VENDOR_ID=0x0416
export PRINTER_PRODUCT_ID=0x5011

# Run the application
uvicorn main:app --reload
```

### Building Docker Image

```bash
docker build -t tactilekanban .
```

### Running with Docker

```bash
docker run -d \
  --name tactilekanban \
  -p 8000:8000 \
  -e PRINTER_VENDOR_ID=0x0416 \
  -e PRINTER_PRODUCT_ID=0x5011 \
  --device=/dev/usb/lp0 \
  tactilekanban
```

## Testing

Currently, there is no automated test suite. When making changes:

1. Test manually by running the application
2. Verify the web form at `http://localhost:8000`
3. Test API endpoints with curl or similar tools
4. If printer hardware is unavailable, test may require mocking

## CI/CD

- GitHub Actions workflow builds and pushes Docker images to GitHub Container Registry
- Images are tagged for branches, PRs, releases, and commit SHAs
- Workflow file: `.github/workflows/docker-build.yml`

## Common Tasks

### Adding New Endpoints

Follow the existing pattern in `main.py`:
- Use appropriate response classes (HTMLResponse, JSONResponse)
- Add proper type hints and docstrings
- Handle errors gracefully with appropriate status codes

### Modifying Print Output

Update the `print_task()` function in `printing.py`:
- Use `_printer.set()` to configure text styling
- Use `_printer.textln()` to print text lines
- Call `_printer.cut()` to cut the receipt after printing

### Supporting Different Printer Types

Modify `_init_printer()` in `printing.py`:
- Import the appropriate printer class from `escpos.printer`
- Adjust initialization parameters as needed
- Update environment variables and documentation accordingly

## Important Notes

- The application must have access to USB devices to function
- Printer initialization fails fast on startup if hardware is not accessible
- Global printer singleton avoids repeated USB initialization overhead
- Unicode text is handled by python-escpos MagicEncode mechanism
- Service worker caches static resources but not POST requests

## Dependencies

Keep dependencies minimal and up-to-date:
- FastAPI and Uvicorn for the web framework
- python-escpos for printer communication
- Jinja2 for templating
- Consider security updates regularly
