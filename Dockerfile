## base image
FROM python:3.10-slim-buster AS base

## install dependencies
# RUN apt update && apt upgrade

## virtualenv
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

## build-image
# FROM base AS builder

RUN pip install --upgrade pip && \
    pip install pip-tools 

# Install necessary packages
RUN apt-get clean && \
    apt-get update && \
    apt-get install -y --reinstall ca-certificates-java cron default-jdk curl g++ gcc && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    update-ca-certificates



WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

#FROM base
# copy Python dependencies from build image
#COPY --from=builder /opt/venv /opt/venv
#ENV PATH="/opt/venv/bin:$PATH"
COPY . /app
WORKDIR /app

EXPOSE 4448
ENTRYPOINT ["gunicorn", "-w", "4", "-b", "0.0.0.0:4448", "app:app", "--timeout", "3600"]
# CMD ["flask", "run", "--port=4444", "--host=0.0.0.0"]