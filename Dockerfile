FROM eclipse-temurin:21-jdk

LABEL authors="yeong"

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3.10 python3-pip \
        chromium-driver \
        chromium \
        libnss3 \
        libxss1 \
        libappindicator1 \
        libindicator7 \
        fonts-liberation \
        libgbm-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN ln -sf /usr/bin/python3.10 /usr/bin/python

ENV PATH="${PATH}:/usr/bin/"

WORKDIR /app
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt --break-system-packages

COPY . .

EXPOSE 8084
# CMD 명령은 파이썬을 사용합니다.
CMD ["python3", "main.py"]