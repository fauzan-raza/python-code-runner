# Stage 1: Extract nsjail from Windmill's image
FROM ghcr.io/windmill-labs/windmill-ee-nsjail:5c4b6e7 as nsjail

# Stage 2: My Python app
FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    libprotobuf32 \
    protobuf-compiler \
    && rm -rf /var/lib/apt/lists/*

# Copy the nsjail binary from the previous stage
COPY --from=nsjail /usr/bin/nsjail /usr/local/bin/nsjail

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
