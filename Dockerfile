FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && python -c "import fastapi, uvicorn, langchain_openai, langchain_core, dotenv"

COPY . .

EXPOSE 8080

CMD ["sh", "-c", "uvicorn Power_Automate.fastapi_webhook:app --host 0.0.0.0 --port ${PORT:-8080}"]
