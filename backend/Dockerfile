# ==========================================
# Builder Stage: Install build dependencies
# ==========================================
FROM python:3.11-slim AS builder

WORKDIR /build

# Avoid writing .pyc files and buffering stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install build dependencies if needed (e.g. gcc, build-essential)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY backend/requirements.txt .
COPY ml/requirements.txt ./ml_requirements.txt
RUN pip install --no-cache-dir --user -r requirements.txt -r ml_requirements.txt

# ==========================================
# Runner Stage: Lean final execution image
# ==========================================
FROM python:3.11-slim AS runner

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH=/root/.local/bin:$PATH

# Copy installed dependencies from builder
COPY --from=builder /root/.local /root/.local

# Copy application source, tests, datasets and ML pipeline
COPY backend/app/ ./app
COPY backend/tests/ ./tests
COPY ml/ ./ml
COPY Dataset/ ./Dataset

# Create a non-privileged user and switch to it for security
RUN useradd -u 10001 appuser && chown -R appuser:appuser /app
USER appuser

# Train the ML model during build so artifacts are baked into the image
RUN python -m ml.train

EXPOSE 8000

# Run uvicorn server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
