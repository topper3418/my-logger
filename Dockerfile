# Use an official Python runtime as a parent image
FROM python:3.11-slim-bullseye

# Set the working directory in the container
WORKDIR /instance

# Copy the current directory contents into the container at /app
COPY . /instance

# install gcc so that the python packages can be installed
RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y \
        gcc \
        build-essential \
        pkg-config 
RUN rm -rf /var/lib/apt/lists/*

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Run app.py when the container launches
CMD ["gunicorn", "app.routes:app", "-b", "0.0.0.0:5000", "--workers=4"]