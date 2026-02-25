FROM python:3.13-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY requirements.txt .
RUN uv pip install --system --no-cache -r requirements.txt \
    && python -c "import fastapi, uvicorn, langchain_openai, langchain_core, dotenv"

COPY . .

EXPOSE 8080

CMD ["sh", "-c", "uvicorn Power_Automate.fastapi_webhook:app --host 0.0.0.0 --port ${PORT:-8080}"]
