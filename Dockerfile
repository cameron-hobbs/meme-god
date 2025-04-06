FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    supervisor \
    git \
 && rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry

COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false && poetry install --no-root --no-interaction --no-ansi

# excessive but it's fine for now
COPY . .

RUN poetry run python manage.py collectstatic --noinput

COPY ./supervisord.conf /etc/supervisor/conf.d/supervisord.conf

CMD ["/usr/bin/supervisord"]
