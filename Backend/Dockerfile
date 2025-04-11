FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run the application
CMD ["sh", "-c", "cd api && uvicorn main:app --host=0.0.0.0 --port=${PORT:-8000}"] 