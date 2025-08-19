FROM mcr.microsoft.com/devcontainers/python:1-3.12-bullseye
RUN apt-get update && apt-get install -y ffmpeg
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
