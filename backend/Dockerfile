FROM python:3.12-slim

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r /app/requirements.txt \
    && playwright install chromium --with-deps

# Install fonts, browser tools, and ffmpeg
RUN apt-get update && apt-get install -y \
    fonts-freefont-ttf \
    fonts-liberation \
    fonts-dejavu \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*
    
RUN playwright install chrome

COPY ./src /app/src
COPY ./tests /app/tests
COPY ./migrations /app/migrations
COPY ./alembic.ini /app/alembic.ini
COPY ./.env /app/.env

ENV PYTHONPATH=/app/src
ENV PATH="/usr/local/bin:${PATH}"

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]