FROM python:3.11

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app /app

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "main_flask_server:app"]