FROM python:3.11-slim
ARG VARIANT
WORKDIR /app
COPY ${VARIANT}/ /app/
RUN pip install --no-cache-dir -r requirements.txt
ENV HOST=0.0.0.0 PORT=5000
EXPOSE 5000
CMD ["python", "app.py"]
