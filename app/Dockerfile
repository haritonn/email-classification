FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .

RUN pip install --no-cache-dir -r 'requirements.txt'
COPY . .

EXPOSE 5000
CMD ["sh", "-c", "flask --app app init-db && flask --app app run --host=0.0.0.0"]