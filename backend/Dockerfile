FROM mcr.microsoft.com/playwright/python:v1.52.0-jammy

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN apt-get update && apt-get install -y ffmpeg

RUN pip install --upgrade pip && pip install -r /app/requirements.txt

COPY ./src /app/src
COPY ./tests /app/tests
COPY ./migrations /app/migrations
COPY ./alembic.ini /app/alembic.ini
COPY ./.env /app/.env

ENV PYTHONPATH=/app/src
ENV PATH="/usr/local/bin:${PATH}"

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
