# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.11-slim-buster


# Set current directory as ENV
ENV PATH=/crawler:$PATH


# Install dependencies
WORKDIR /crawler
COPY requirements.txt ./requirements.txt
RUN python3.11 -m pip install --upgrade pip
RUN pip install -r requirements.txt


# Virtual Display
RUN apt update
RUN apt install -y tigervnc-standalone-server default-jre wget


# Install chrome
RUN wget http://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_114.0.5735.198-1_amd64.deb
RUN apt install -y ./google-chrome-stable_114.0.5735.198-1_amd64.deb unzip


# Download chromedriver
# RUN wget https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip
# RUN unzip chromedriver_linux64.zip


# Copying required items
COPY ad-crawler.py ./ad-crawler.py
# ADD code ./code
# ADD consent-extension ./consent-extension
# ADD data ./data
# ADD output ./output
