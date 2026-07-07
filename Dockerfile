# Container image for OCR BookFinder. Works on Hugging Face Spaces (Docker SDK, port 7860)
# and any Docker host.
FROM python:3.11-slim

# System deps: Tesseract for OCR, libGL/glib for OpenCV.
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Writable locations for the response cache and uploads (world-writable so the app works
# whether the container runs as root or an unprivileged user, as on HF Spaces).
ENV BOOKFINDER_CACHE_DIR=/tmp/bookfinder_cache
RUN mkdir -p /tmp/bookfinder_cache static/uploads && chmod -R 777 /tmp/bookfinder_cache static

EXPOSE 7860

# Production WSGI server. Full-text page search makes several outbound calls, so allow a
# generous per-request timeout.
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "--workers", "2", "--timeout", "180", "app:app"]
