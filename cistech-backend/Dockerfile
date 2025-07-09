# Use an official Python runtime as a parent image
FROM python:3.13-slim

RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*
# Set environment variables
ENV PYTHONUNBUFFERED=1
ARG DATABASE_URL
ARG TWILIO_ACCOUNT_SID
ARG TWILIO_AUTH_TOKEN
ARG TWILIO_PHONE_NUMBER
ARG TWILIO_VERIFY_SERVICE_SID

ENV DATABASE_URL=$DATABASE_URL
ENV TWILIO_ACCOUNT_SID=$TWILIO_ACCOUNT_SID
ENV TWILIO_AUTH_TOKEN=$TWILIO_AUTH_TOKEN
ENV TWILIO_PHONE_NUMBER=$TWILIO_PHONE_NUMBER
ENV TWILIO_VERIFY_SERVICE_SID=$TWILIO_VERIFY_SERVICE_SID


# Set the working directory in the container
WORKDIR /app


# Install system dependencies. 
# psycopg2 requires libpq-dev to be installed.
RUN apt-get update && apt-get install -y libpq-dev && rm -rf /var/lib/apt/lists/*

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# We upgrade pip and use --no-cache-dir to keep the image slim
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt


# Copy the rest of the application's code to the working directory
# The .dockerignore file will prevent copying local dev files
COPY . .

EXPOSE 8080

# The application will be started by running main.py
# which is configured to listen on the port specified by the PORT env var.
# Cloud Run injects this variable. The default for Cloud Run is 8080.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"] 