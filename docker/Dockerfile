FROM python:3.11-slim

WORKDIR /app

COPY app/ .

RUN pip install --no-cache-dir -r requirements.txt

# Create the database before starting Flask
RUN python database.py

EXPOSE 5000

CMD ["python", "app.py"]