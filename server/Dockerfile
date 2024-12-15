FROM python:3.10-bookworm

ARG DEBIAN_FRONTEND=noninteractive

# Create log directories with proper permissions
RUN mkdir -p /app/logs && \
    touch /app/logs/whisperlive.log && \
    touch /app/logs/connections.log && \
    chmod 666 /app/logs/whisperlive.log && \
    chmod 666 /app/logs/connections.log

# install lib required for pyaudio
RUN apt update && apt install -y portaudio19-dev && apt-get clean && rm -rf /var/lib/apt/lists/*

# update pip to support for whl.metadata -> less downloading
RUN pip install --no-cache-dir -U "pip>=24"

# create a working directory
WORKDIR /app

# install the requirements for running the whisper-live server
COPY requirements/server.txt /app/
RUN pip install -r server.txt && rm server.txt

# make the paths of the nvidia libs installed as wheels visible. equivalent to:
# export LD_LIBRARY_PATH=`python3 -c 'import os; import nvidia.cublas.lib; import nvidia.cudnn.lib; print(os.path.dirname(nvidia.cublas.lib.__file__) + ":" + os.path.dirname(nvidia.cudnn.lib.__file__))'`
ENV LD_LIBRARY_PATH="/usr/local/lib/python3.10/site-packages/nvidia/cublas/lib:/usr/local/lib/python3.10/site-packages/nvidia/cudnn/lib"

COPY whisper_live /app/whisper_live
COPY run_server.py /app

# Copy application files
EXPOSE ${PORT_WHISPERLIVE}
ARG PORT_WHISPERLIVE
ENV PORT_WHISPERLIVE=${PORT_WHISPERLIVE}
ARG FASTERWHISPER_MODEL
ENV FASTERWHISPER_MODEL=${FASTERWHISPER_MODEL}
ARG WHISPERLIVE_SSL
ENV WHISPERLIVE_SSL=${WHISPERLIVE_SSL}

CMD ["sh", "-c", "\
    if [ \"$WHISPERLIVE_SSL\" = \"true\" ]; then \
        python3 -u run_server.py --port $PORT_WHISPERLIVE --backend faster_whisper --faster_whisper_custom_model_path /app/models/$FASTERWHISPER_MODEL --ssl_cert_path /app/ssl; \
    else \
        python3 -u run_server.py --port $PORT_WHISPERLIVE --backend faster_whisper --faster_whisper_custom_model_path /app/models/$FASTERWHISPER_MODEL; \
    fi"]
