FROM python:3.11-slim
WORKDIR /app
COPY ./auth_service /app
COPY ./requirements.txt requirements.txt
COPY ./shared /app/shared
COPY .env /app
RUN pip install --no-cache-dir -r requirements.txt
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]