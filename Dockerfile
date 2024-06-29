# Use the Python 3.11 image as base
FROM python:3.11

# Set the working directory in the container
WORKDIR /app

# Copy requirements.txt to the working directory
COPY ./requirements.txt .

# Install Python dependencies
RUN pip install -r requirements.txt

# Copy entrypoint.py to the working directory
COPY ./entrypoint.py .

# Expose the port that Flask runs on
EXPOSE 5000

# Specify the command to run your Flask app using Gunicorn
CMD exec gunicorn entrypoint:app -b 0.0.0.0:5000 --reload
