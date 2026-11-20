FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    DATABASE_URL=sqlite:////app/aura.db

WORKDIR /app

RUN groupadd --system aura && useradd --system --gid aura --create-home --home-dir /home/aura aura

COPY requirements-local.txt ./
RUN pip install --no-cache-dir --disable-pip-version-check -r requirements-local.txt

COPY --chown=aura:aura app ./app
RUN chown -R aura:aura /app

USER aura

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3)"

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
