FROM python:3.12.11-bookworm
WORKDIR /app
RUN apt-get update && apt-get install -y ffmpeg
COPY requirements.txt .
COPY main.py .
RUN pip install -r requirements.txt
CMD ["python", "main.py"]
