FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Download prebuilt nsjail 3.4 binary and make executable
RUN curl -L https://github.com/google/nsjail/releases/download/3.4/nsjail-3.4-linux-amd64 -o /usr/local/bin/nsjail \
    && chmod +x /usr/local/bin/nsjail

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
