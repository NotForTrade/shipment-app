#FROM alpine:latest
FROM python:3.12-alpine 

WORKDIR /usr/src/app

#RUN apk add --update python3 py3-pip

COPY . /usr/src/app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["python", "app.py"]