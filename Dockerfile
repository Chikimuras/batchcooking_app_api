FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

# Install minimal system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates \
 && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set working directory inside the container
WORKDIR /app

# Copy dependency files first for better Docker layer caching
COPY pyproject.toml uv.lock ./

# Create virtual environment and install dependencies
RUN uv venv && uv pip install --upgrade pip && uv sync --frozen --no-cache

# Copy the rest of the application code
COPY . .

# Expose port (optional, for documentation purposes)
EXPOSE 80

# Start the FastAPI app using the FastAPI CLI (from fastapi[standard])
CMD ["/app/.venv/bin/fastapi", "run", "app/main.py", "--host", "0.0.0.0", "--port", "80"]
