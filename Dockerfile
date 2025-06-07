FROM python:3.12-slim

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Créer un utilisateur sécurisé
RUN useradd --create-home --shell /bin/bash appuser

# Copy the application into the container.
COPY . /app
WORKDIR /app

# Installer les dépendances (crée automatiquement .venv)
RUN uv sync --frozen --no-cache

# Droits utilisateur
RUN chown -R appuser:appuser /app
USER appuser

# Run the application.
CMD ["/app/.venv/bin/fastapi", "run", "app/main.py", "--port", "80", "--host", "0.0.0.0"]
