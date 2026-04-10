FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for lxml
RUN apt-get update && apt-get install -y \
    gcc \
    libxml2-dev \
    libxslt-dev \
    && rm -rf /var/lib/apt/lists/*

# Install local packages first
COPY ../core /packages/core
COPY ../services /packages/services
RUN pip install --no-cache-dir -e /packages/core -e /packages/services

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
