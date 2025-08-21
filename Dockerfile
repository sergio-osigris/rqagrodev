FROM python:3.12

# Update package lists and install system dependencies
RUN apt-get update && \
    apt-get install -y \
    g++ \
    make && rm -rf /var/lib/apt/lists/*

# RUN curl -sSL https://install.python-poetry.org | python3 -

ENV YOUR_ENV=${YOUR_ENV} \
  PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  # Poetry's configuration:
  POETRY_NO_INTERACTION=1 \
  POETRY_VIRTUALENVS_CREATE=false \
  POETRY_CACHE_DIR='/var/cache/pypoetry' \
  POETRY_HOME='/usr/local' \
  POETRY_VERSION=1.8.2

RUN pip install "poetry==1.8.4" "fastapi[standard]"

WORKDIR /app

# Copy ONLY dependency files first
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry install --only main --no-interaction --no-ansi

COPY . .

EXPOSE 8000

CMD exec uvicorn app.main:app --host 0.0.0.0 --port 8000