FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt .

RUN apt-get update -y && \
    apt-get upgrade -y 

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

COPY . .

CMD ["python", "app.py"]