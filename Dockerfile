FROM python:3.10-alpine

RUN apk add sqlite
RUN pip3 install pipenv

WORKDIR /app

COPY . .
RUN pipenv install

EXPOSE 8080

ENTRYPOINT ["pipenv", "run", "python", "app.py"]
