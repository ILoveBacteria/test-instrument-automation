# Use the official Python image as the base image
FROM docker.arvancloud.ir/python:3.13-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose the default Streamlit port
EXPOSE 8501

# Command to run the Streamlit app
ENTRYPOINT [ "streamlit", "run" ]

CMD ["live_dashboard.py"]
