FROM python:3.11-slim

WORKDIR /notification

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ./notification ./notification

EXPOSE 8000

CMD ["fastapi", "dev", "main.py", "--host", "0.0.0.0", "--port", "8000"]




