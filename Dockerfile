FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py config.py README.md ./
COPY src ./src
COPY static ./static
COPY scripts ./scripts
COPY reports ./reports
COPY docs ./docs

EXPOSE 8000
CMD ["sh", "scripts/start.sh"]
