# ============================================================
# NEXORA MARKET — single-image deploy (API + website together)
# Build:  docker build -t nexora-market .
# Run:    docker run -p 8000:8000 --env-file backend/.env nexora-market
# Open:   http://localhost:8000/
# ============================================================
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /srv

# Install backend dependencies
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy backend code + frontend assets
COPY backend/ ./backend/
COPY index.html ./index.html
COPY assets/ ./assets/

# main.py resolves the project root as two levels up from app/main.py
# (i.e. /srv), where index.html and assets/ live.
WORKDIR /srv/backend

EXPOSE 8000
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
