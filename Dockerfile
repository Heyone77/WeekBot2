FROM python:3.10.10-alpine3.16

RUN mkdir -p /app
WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

CMD [ "python3", "-m" , "main" ]