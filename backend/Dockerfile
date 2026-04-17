FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (ffmpeg is heavily needed)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install poetry
RUN pip install --no-cache-dir poetry

# Copy pyproject.toml
COPY pyproject.toml poetry.lock* ./

# Configure poetry to not use a virtualenv inside the container,
# but install packages into system python
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --no-root

# Copy app source
COPY app/ app/

# Command to run via uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
