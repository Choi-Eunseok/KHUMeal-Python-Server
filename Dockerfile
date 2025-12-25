FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
COPY build_proto.sh ./build_proto.sh
COPY proto/ ./proto/
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libgl1 \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        libxrender-dev \
        gcc \
        && rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir -r requirements.txt && \
    chmod +x build_proto.sh && ./build_proto.sh

COPY . .

EXPOSE 50051

CMD ["python", "grpc_server.py"]
