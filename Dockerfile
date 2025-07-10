FROM ghcr.io/windmill-labs/windmill-ee-nsjail:5c4b6e7 AS nsjail
FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    libprotobuf32 \
    libnl-route-3-200 \
    && rm -rf /var/lib/apt/lists/

COPY --from=nsjail /usr/bin/nsjail /usr/local/bin/nsjail
RUN chmod +x /usr/local/bin/nsjail

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY nsjail.cfg /nsjail.cfg 

EXPOSE 8080
ENV FLASK_APP=app.main
CMD ["flask", "run", "--host=0.0.0.0", "--port=8080"]