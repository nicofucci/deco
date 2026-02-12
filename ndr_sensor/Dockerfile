FROM python:3.11-slim

# Install system tools
RUN apt-get update && apt-get install -y \
    arp-scan \
    nmap \
    iproute2 \
    avahi-utils \
    net-tools \
    nbtscan \
    iputils-ping \
    dnsutils \
    snmp \
    libpcap-dev \
    gcc \
    g++ \
    make \
    python3-dev \
    libc6-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
RUN mkdir -p /logs && chmod 777 /logs

COPY requirements.txt .
RUN python -m pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

# Environment variables
ENV PYTHONUNBUFFERED=1

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "18150"]
