FROM python:3.10-slim-buster

ENV LANG=C.UTF-8
ENV TZ=UTC

RUN apt-get update && apt-get install -y --no-install-recommends \
  ghostscript \
  jbig2dec \
  img2pdf \
  libsm6 libxext6 libxrender-dev \
  pngquant \
  tesseract-ocr \
  tesseract-ocr-chi-sim \
  tesseract-ocr-deu \
  tesseract-ocr-eng \
  tesseract-ocr-fra \
  tesseract-ocr-por \
  tesseract-ocr-spa \
  unpaper \
  && rm -rf /var/lib/apt/lists/*

RUN groupadd -r ocrmypdf && useradd --no-log-init -r -m -g ocrmypdf ocrmypdf
USER ocrmypdf

ADD --chown=ocrmypdf:ocrmypdf 'https://install.python-poetry.org' poetry-install.sh
RUN python poetry-install.sh

WORKDIR /app

COPY poetry.lock pyproject.toml main.py app.py ./

ENV PATH="/home/ocrmypdf/.local/bin:$PATH"

RUN poetry install --only main

ENTRYPOINT ["poetry", "run", "python", "main.py"]
