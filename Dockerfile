# Dockerfile
FROM python:3.10-slim

# Set workdir
WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y \
    build-essential libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . /app/

# Expose Django port
EXPOSE 8000

# Default command (overridden by docker-compose)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
