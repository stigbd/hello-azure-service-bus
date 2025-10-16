FROM python:3.14-slim

RUN apt-get update && apt-get install -y \
    build-essential curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy the application into the container.
ADD /receiver /app

# Install the application dependencies.
WORKDIR /app

RUN uv sync --frozen

# Expose the application port.
EXPOSE 8000

CMD ["uv", "run", "src/receiver.py"]
