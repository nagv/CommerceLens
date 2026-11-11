FROM python:3.12-slim AS base
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
FROM base AS test
COPY tests tests
RUN python -m unittest discover -s tests -v
FROM base AS runtime
RUN useradd --uid 10001 --create-home app
USER app
EXPOSE 8080
CMD ["uvicorn","app:app","--host","0.0.0.0","--port","8080"]
