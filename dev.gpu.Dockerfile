ARG CUDA_VERSION="11.8.0"
ARG CUDNN_VERSION="8"
ARG UBUNTU_VERSION="22.04"
ARG MAX_JOBS=4

FROM nvidia/cuda:$CUDA_VERSION-cudnn$CUDNN_VERSION-devel-ubuntu$UBUNTU_VERSION

RUN mkdir -p /app/storage && ln -s /storage /app/storage # backward compatibility for (https://github.com/CatchTheTornado/text-extract-api/issues/85)

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    wget \
    curl \
    unzip \
    git \
    python3 \
    python3-pip \
    libgl1 \
    libglib2.0-0 \
    libglib2.0-dev \
    curl \
    gnupg2 \
    ca-certificates \
    apt-transport-https \
    software-properties-common \
    libreoffice \
    libmagic1 \
    libmagic-dev \
    ffmpeg \
    git-lfs \
    xvfb \
    && ln -s /usr/bin/python3 /usr/bin/python \
    && apt-get update \
    && apt install python3-packaging \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

WORKDIR /app

RUN echo 'Acquire::http::Pipeline-Depth 0;\nAcquire::http::No-Cache true;\nAcquire::BrokenProxy true;\n' > /etc/apt/apt.conf.d/99fixbadproxy

RUN apt-get clean && rm -rf /var/lib/apt/lists/* \
    && apt-get update --fix-missing \
    && apt-get install -y \
        libgl1 \
        poppler-utils \
        libpoppler-cpp-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

EXPOSE 8000

ENTRYPOINT ["/app/scripts/entrypoint.sh"]
