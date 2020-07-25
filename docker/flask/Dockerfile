FROM python:3.8

ARG SRC_DIR="./apps"
ARG DOCKER_DIR="./docker/flask"
ARG APP_DIR="/apps"

RUN mkdir ${APP_DIR}

COPY "${DOCKER_DIR}/entrypoint.sh" "/entrypoint.sh"
ADD "${SRC_DIR}" "${APP_DIR}"

WORKDIR ${APP_DIR}

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
#    python-pyaudio \
#    python3-pyaudio \
#    portaudio19-dev \
    ffmpeg \
 && apt-get -y clean \
 && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip --no-cache-dir
RUN pip install -r requirements.txt --no-cache-dir

EXPOSE 5000

ENV PYTHONPATH "${PYTHONPATH}:${APP_DIR}/"
ENV FLASK_APP "${APP_DIR}/run.py"

CMD ["sh", "/entrypoint.sh"]