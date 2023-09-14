## base image
FROM python:3.9.9-slim-buster AS base

RUN apt-get update && \
    apt-get install -y --no-install-recommends default-jdk && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

# Verify Java installation
RUN java -version

COPY . /app
WORKDIR /app

EXPOSE 4448
CMD ["gunicorn", "-b 0.0.0.0:4448", "--workers", "1", "--timeout", "1800", "app:app", "--reload"]
# CMD ["flask", "run", "--port=4444", "--host=0.0.0.0"]