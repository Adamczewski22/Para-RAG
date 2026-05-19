FROM python:3.11-slim

WORKDIR /app

# Makes Python print logs immediately instead of buffering
ENV PYTHONUNBUFFERED=1
# Prevents pycache and .pyc files
ENV PYTHONDONTWRITEBYTECODE=1

COPY requirements/core.txt .
COPY requirements/server.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r core.txt \
    && pip install --no-cache-dir -r server.txt

COPY pararag ./pararag
COPY pararag_server ./pararag_server

EXPOSE 8000

CMD ["uvicorn", "pararag_server.endpoints:app", "--host", "0.0.0.0", "--port", "8000"]