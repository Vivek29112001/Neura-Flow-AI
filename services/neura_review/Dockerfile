FROM python:3.11-slim

WORKDIR /app

COPY services/shared/requirements.txt /tmp/req-shared.txt
RUN pip install --no-cache-dir -r /tmp/req-shared.txt

COPY services/shared /app/services/shared
COPY services/neura_review /app/services/neura_review
RUN touch /app/services/__init__.py

ENV PYTHONPATH=/app
EXPOSE 8005

CMD ["uvicorn", "services.neura_review.main:app", "--host", "0.0.0.0", "--port", "8005"]
