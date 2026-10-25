FROM python:3.11-slim
ARG VARIANT
ARG PIP_FLAGS=""
WORKDIR /app
COPY ${VARIANT}/ /app/
RUN pip install --no-cache-dir ${PIP_FLAGS} -r requirements.txt
EXPOSE 5000
CMD ["python", "app.py"]
