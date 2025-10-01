FROM python:3.11-slim AS base

# Avoid Python writing .pyc files to disk
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . /app/

# Set default environment variables (can be overridden at runtime)
ENV PRINTER_VENDOR_ID=0x0416
ENV PRINTER_PRODUCT_ID=0x5011
ENV PRINTER_INTERFACE=0

EXPOSE 8000

# Use uvicorn to serve FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]