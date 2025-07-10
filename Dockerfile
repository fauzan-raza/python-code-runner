FROM python:3.9-slim

# Install build dependencies and tools needed for nsjail and python packages
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    bison \
    flex \
    protobuf-compiler \
    pkg-config \
    libseccomp-dev \
    libprotobuf-dev \
    libcap-dev \
    libselinux1-dev \
    && rm -rf /var/lib/apt/lists/*

# Clone and build nsjail
RUN git clone https://github.com/google/nsjail.git /nsjail \
    && cd /nsjail \
    && make

ENV PATH="/nsjail:${PATH}"

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
