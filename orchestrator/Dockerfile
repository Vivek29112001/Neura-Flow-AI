FROM python:3.11-slim

WORKDIR /app

COPY orchestrator/requirements.txt /tmp/req.txt
RUN pip install --no-cache-dir -r /tmp/req.txt

COPY services/shared /app/services/shared
COPY orchestrator /app/orchestrator
RUN touch /app/services/__init__.py

ENV PYTHONPATH=/app
EXPOSE 8000

CMD ["uvicorn", "orchestrator.main:app", "--host", "0.0.0.0", "--port", "8000"]
