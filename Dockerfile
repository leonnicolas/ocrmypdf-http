FROM jbarlow83/ocrmypdf

WORKDIR /usr/lib/http

RUN apt-get update && apt-get install curl python3 python3-distutils -y

RUN groupadd -r ocrmypdf && useradd --no-log-init -r -m -g ocrmypdf ocrmypdf
USER ocrmypdf

RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3 -

COPY poetry.lock pyproject.toml main.py app.py ./

ENV PATH=$PATH:/home/ocrmypdf/.poetry/bin

RUN poetry install --no-dev

ENTRYPOINT ["poetry", "run", "python", "main.py"]
