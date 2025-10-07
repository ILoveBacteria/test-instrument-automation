# Use the official Python image as the base image
FROM docker.arvancloud.ir/python:3.13-slim

# Set the working directory in the container
WORKDIR /app

# Install git for pip to install packages from git repositories
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose the default Streamlit port
EXPOSE 5000

# Command to run the Streamlit app
ENTRYPOINT [ "python", "api_server.py" ]
