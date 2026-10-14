FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY Utils/Region ./Utils/Region

EXPOSE 8000

CMD ["uvicorn", "restaurant_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
