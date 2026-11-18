
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .
COPY frontend/public/ /frontend/public/

# Create a dedicated non-root application user.
RUN useradd --system --create-home appuser \
    && mkdir -p /app/storage \
    && chown -R appuser:appuser /app

# Run the application without root privileges.
USER appuser

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
