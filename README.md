# tactilekanban
Prints thermal slips to create physical kanban board in meatspace

## Docker Usage

### Pull the Docker Image

```bash
docker pull ghcr.io/mixmastrbrock/tactilekanban:main
```

### Run the Container

```bash
docker run -d \
  --name tactilekanban \
  -p 8000:8000 \
  -e PRINTER_VENDOR_ID=0x0416 \
  -e PRINTER_PRODUCT_ID=0x5011 \
  -e PRINTER_INTERFACE=0 \
  --device=/dev/usb/lp0 \
  ghcr.io/mixmastrbrock/tactilekanban:main
```

**Note:** Replace the environment variables with your specific printer's USB vendor ID, product ID, and interface. The `--device` flag grants the container access to your USB printer.

### Environment Variables

- `PRINTER_VENDOR_ID` (required): USB vendor ID for the thermal printer (e.g., `0x0416`)
- `PRINTER_PRODUCT_ID` (required): USB product ID for the thermal printer (e.g., `0x5011`)
- `PRINTER_INTERFACE` (optional): USB interface number (default: `0`)
- `PRINTER_PROFILE` (optional): Name of the printer profile from the python-escpos profiles database

### Access the Application

Once running, navigate to `http://localhost:8000` in your web browser to access the task printing interface.
