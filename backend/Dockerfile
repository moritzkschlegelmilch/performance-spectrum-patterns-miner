# Use an official Python runtime as the base image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container
COPY . /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN mv app/env.example.py app/env.py

# Expose the port the app will run on
EXPOSE 8000

# Set the environment variable to tell Python to run in unbuffered mode
ENV PYTHONUNBUFFERED=1

# Command to run the app and apply migrations
CMD cd app && alembic upgrade head && uvicorn main:app --reload --host 0.0.0.0 --port 8000