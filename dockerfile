# Use the official Python image as the base image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Define build arguments

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir --default-timeout=100 --retries=10 -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

EXPOSE 8080

# Specify the command to run the application
CMD ["python", "run.py"]
