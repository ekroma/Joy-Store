FROM python:3.10

RUN groupadd -r globalgroup && useradd -r -g globalgroup globaluser

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libglib2.0-0 \
    libgl1-mesa-glx\
    ca-certificates \
    && update-ca-certificates 2>/dev/null || true


RUN apt-get update -y \
    && apt-get upgrade -y \
    && apt-get install -y sudo nano \
    && pip install --upgrade pip \
    && rm -rf /var/lib/apt/lists/*


RUN mkdir -p /var/www/public/media/ && chmod -R 777 /var/www/public/media/

RUN mkdir -p /db/backups/
RUN mkdir -p /app/backend3/src3/migrations/versions/


COPY ./requirements/dev.txt ./
RUN pip install --no-cache-dir --upgrade -r dev.txt

COPY ./src ./src
RUN chown -R globaluser:globalgroup /app
RUN echo 'globaluser:liDeraYStRiC' | chpasswd
USER globaluser
