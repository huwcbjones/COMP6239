FROM python:3.6-alpine

ADD https://github.com/ufoscout/docker-compose-wait/releases/latest/download/wait /wait
RUN chmod +x /wait

RUN adduser -D comp6239
RUN pip install --upgrade pip && pip install pipenv
RUN apk update && apk add --no-cache openssl-dev libffi-dev build-base postgresql-dev python3-dev musl-dev

RUN mkdir /app
COPY Pipfile* /app/

WORKDIR /app
RUN pipenv install --deploy --system
RUN apk del build-base

COPY . /app
RUN chown -R root:root .

USER comp6239

EXPOSE 8080
CMD /wait && python3 -O comp6239.py