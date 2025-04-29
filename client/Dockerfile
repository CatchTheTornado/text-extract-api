# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory
WORKDIR /client

# Install system dependencies
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Define the command to run the CLI script
CMD ["python", "cli.py"]
