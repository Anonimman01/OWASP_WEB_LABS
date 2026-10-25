FROM python:3.11-slim
ARG VARIANT
WORKDIR /app
COPY ${VARIANT}/ /app/
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5000
CMD ["python", "app.py"]
