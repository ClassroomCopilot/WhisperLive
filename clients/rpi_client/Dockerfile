FROM tailscale/tailscale:latest

# Install necessary packages including build tools
RUN apk update && apk add --no-cache \
    portaudio-dev \
    alsa-lib-dev \
    alsa-utils \
    gcc \
    g++ \
    python3 \
    py3-pip \
    python3-dev \
    iproute2 \
    ffmpeg \
    ffmpeg-dev \
    pkgconfig

# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Copy the start script and make it executable
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Command to run the start script
CMD ["/bin/sh", "/app/start.sh"]