FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive

# Systémové závislosti (přidány chybějící knihovny)
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    libmagic-dev \
    libglib2.0-dev \
    poppler-utils \
    ghostscript \
    ffmpeg \
    pkg-config \
    automake \
    autoconf \
    libtool \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . .

# Základní build nástroje (pro PEP 517 – pyproject.toml)
RUN pip install --upgrade pip setuptools wheel build

# Instalace projektu
RUN pip install .

RUN chmod +x run.sh

CMD ["bash", "run.sh"]
