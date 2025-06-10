FROM mcr.microsoft.com/playwright/python:v1.52.0-jammy

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

# RUN apt-get update && apt-get install -y ffmpeg

# RUN pip install --upgrade pip && pip install -r /app/requirements.txt \
#     && playwright install chromium chrome --with-deps

RUN apt-get update && apt-get install -y \
    ffmpeg libsm6 libxext6 libxrender1 libglib2.0-0

RUN pip uninstall -y yt-dlp && \
    pip install -U --pre -f https://github.com/yt-dlp/yt-dlp-nightly-builds/releases/latest yt-dlp

RUN pip uninstall -y opencv-python opencv-python-headless && \
    pip install opencv-python-headless==4.9.0.80

COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r /app/requirements.txt && \
    playwright install chromium chrome --with-deps

COPY ./src /app/src
COPY ./tests /app/tests
COPY ./migrations /app/migrations
COPY ./alembic.ini /app/alembic.ini
COPY ./.env /app/.env

ENV PYTHONPATH=/app/src
ENV PATH="/usr/local/bin:${PATH}"

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
