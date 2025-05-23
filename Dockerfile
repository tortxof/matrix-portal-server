FROM python:3.13.3

COPY --from=ghcr.io/astral-sh/uv:0.7.7 /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock app.py /app/

RUN uv sync --locked && \
    uv run python -c 'from skyfield.api import load; load("de421.bsp")'

CMD ["uv", "run", "gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "--access-logfile=-", "app:app"]
