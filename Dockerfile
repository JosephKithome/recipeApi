FROM python:3.9-alpine

LABEL maintainer ="SoftDev Solutions Ltd"

ENV PYTHONUNBUFFERED 1

ENV PATH="/scripts:${PATH}"

COPY ./requirements.txt /requirements.txt

RUN apk add --update --no-cache postgresql-client jpeg-dev

RUN apk add --update --no-cache --virtual .temp-build-deps \
    gcc libc-dev linux-headers postgresql-dev musl-dev zlib zlib-dev

RUN python -m pip install --upgrade pip && \
     pip install -r requirements.txt

RUN apk del .temp-build-deps

RUN mkdir /app

WORKDIR /app


COPY ./app /app

COPY ./scripts /scripts

RUN chmod +x /scripts/*



RUN mkdir -p /vol/web/media

RUN mkdir -p /vol/web/static

RUN adduser -D user

RUN chown -R user:user /vol/

RUN chmod -R 755 /vol/web

USER user

CMD ["entrypoint.sh"]
