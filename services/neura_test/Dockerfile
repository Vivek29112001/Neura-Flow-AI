FROM python:3.11-slim

WORKDIR /app

COPY services/shared/requirements.txt /tmp/req-shared.txt
RUN pip install --no-cache-dir -r /tmp/req-shared.txt pytest pytest-asyncio httpx

COPY services/shared /app/services/shared
COPY services/neura_test /app/services/neura_test
RUN touch /app/services/__init__.py

ENV PYTHONPATH=/app
EXPOSE 8003

CMD ["uvicorn", "services.neura_test.main:app", "--host", "0.0.0.0", "--port", "8003"]
