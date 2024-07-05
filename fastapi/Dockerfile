# fastapi/Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY fastapi/requirements.txt /app/fastapi/
RUN pip install --no-cache-dir -r /app/fastapi/requirements.txt

COPY fastapi /app/fastapi

WORKDIR /app/fastapi
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]