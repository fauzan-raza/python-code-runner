FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    nsjail \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY nsjail.cfg .

EXPOSE 8080

ENV FLASK_APP=app.main
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=8080

CMD ["flask", "run"]
