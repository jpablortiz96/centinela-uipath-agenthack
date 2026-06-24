FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run the runtime api
CMD ["sh", "-c", "uvicorn apps.centinela_runtime.main:app --host 0.0.0.0 --port ${PORT:-8070}"]
