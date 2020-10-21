FROM python:3.7-alpine
WORKDIR /code
ENV PYTHONUNBUFFERED=0
RUN apk add --no-cache gcc musl-dev linux-headers jpeg-dev zlib-dev freetype-dev lcms2-dev openjpeg-dev tiff-dev tk-dev tcl-dev
COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock
RUN pip install pipenv && pipenv install --system
COPY . .
