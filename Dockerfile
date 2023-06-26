FROM python:3.10

# Install Chrome and chromedriver
RUN apt-get update && apt-get install -y wget gnupg
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list
RUN apt-get update && apt-get install -y google-chrome-stable
RUN wget https://chromedriver.storage.googleapis.com/94.0.4606.61/chromedriver_linux64.zip
RUN unzip chromedriver_linux64.zip && mv chromedriver /usr/local/bin/

# Set the working directory
WORKDIR /app

# Copy the requirements file and install the dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the source code into the container
COPY . .

# Expose port 8081 for the webui
EXPOSE 8080

# Run the script
CMD ["python", "webui.py"]