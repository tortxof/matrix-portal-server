FROM python:3.11.6

ENV POETRY_HOME=/opt/poetry

RUN python -m venv $POETRY_HOME \
    && $POETRY_HOME/bin/pip install poetry==1.7.0 \
    && $POETRY_HOME/bin/poetry --version

ENV PATH="${POETRY_HOME}/bin:${PATH}"

WORKDIR /app

COPY pyproject.toml poetry.lock app.py /app/

RUN poetry install \
    && poetry run python -c 'from skyfield.api import load; load("de421.bsp")'

CMD ["poetry", "run", "gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "--access-logfile=-", "app:app"]
