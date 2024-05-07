FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt .

RUN apt-get update -y && \
    apt-get upgrade -y && \
    apt-get install -y unzip

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

COPY . .

# Unzip the pre-trained topic model
RUN unzip data/topic_newshour.zip -d data/

CMD ["python", "app.py"]