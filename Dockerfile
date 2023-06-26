FROM python:3.10

# Install Chrome and chromedriver
RUN apt-get update && apt-get install -y wget gnupg
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list
RUN apt-get update && apt-get install -y google-chrome-stable
RUN wget https://chromedriver.storage.googleapis.com/LATEST_RELEASE
RUN wget https://chromedriver.storage.googleapis.com/$(cat LATEST_RELEASE)/chromedriver_linux64.zip
RUN unzip chromedriver_linux64.zip && mv chromedriver /usr/local/bin/

# Create a new user to run the webui
RUN useradd -ms /bin/bash webuiuser

# Set the working directory and change ownership to the new user
WORKDIR /app
RUN chown -R webuiuser:webuiuser /app

# Switch to the new user
USER webuiuser

# Copy the requirements file and install the dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the source code into the container
COPY . .

# Expose port 8081 for the webui
EXPOSE 8080

# Run the script
CMD ["python", "webui.py"]