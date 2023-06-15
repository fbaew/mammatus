# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Install nginx and curl
RUN apt-get update && apt-get install -y nginx curl

# Copy the nginx configuration file
COPY nginx.conf /etc/nginx/nginx.conf
# Install Chrome and chromedriver
RUN apt-get update && apt-get install -y wget gnupg2
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list
RUN apt-get update && apt-get install -y google-chrome-stable
RUN wget -N https://chromedriver.storage.googleapis.com/$(curl -sS https://chromedriver.storage.googleapis.com/LATEST_RELEASE)/chromedriver_linux64.zip -P /tmp/
RUN unzip /tmp/chromedriver_linux64.zip -d /usr/bin/
RUN chmod +x /usr/bin/chromedriver

# Copy the cron job file
COPY cron /etc/cron.d/cron

# Give execution rights on the cron job file
RUN chmod 0644 /etc/cron.d/cron

# Apply the cron job
RUN crontab /etc/cron.d/cron

# Make port 88 available to the world outside this container
EXPOSE 88

# Start the Flask server
CMD python webui.py & nginx -g "daemon off;"