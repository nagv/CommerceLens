FROM python:3.12-slim
WORKDIR /app
COPY server.py .
RUN useradd --uid 10001 --create-home app && mkdir /data && chown app:app /data
USER app
EXPOSE 8080
CMD ["python", "-u", "server.py"]
