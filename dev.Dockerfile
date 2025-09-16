FROM python:3.10-slim

RUN mkdir -p /app/storage && ln -s /storage /app/storage # backward compability for (https://github.com/CatchTheTornado/text-extract-api/issues/85)

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libglib2.0-0 \
        libglib2.0-dev \
        libgl1 \
        poppler-utils \
        libmagic1 \
        libmagic-dev \
        libpoppler-cpp-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

EXPOSE 8000

ENTRYPOINT ["/app/scripts/entrypoint.sh"]
