FROM python:3.11-slim

WORKDIR /app

# Install shared + service deps
COPY services/shared/requirements.txt /tmp/req-shared.txt
RUN pip install --no-cache-dir -r /tmp/req-shared.txt

# Copy source
COPY services/shared /app/services/shared
COPY services/neura_architect /app/services/neura_architect
RUN touch /app/services/__init__.py

ENV PYTHONPATH=/app
EXPOSE 8001

CMD ["uvicorn", "services.neura_architect.main:app", "--host", "0.0.0.0", "--port", "8001"]
