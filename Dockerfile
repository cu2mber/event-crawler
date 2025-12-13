FROM debian:bullseye

LABEL authors="yeong"

RUN apt-get update && \
    apt-get install -y --no-install-recommends --fix-missing \
        python3 python3-pip \
        wget gnupg curl \
        openjdk-17-jdk \
        chromium chromium-driver \
        libnss3 libxss1 libgbm-dev fonts-liberation libasound2 libatk1.0-0 libgtk-3-0 libappindicator3-1 \
        xdg-utils libwoff1 fonts-dejavu libgdk-pixbuf2.0-0 libharfbuzz-icu0 libcurl4 libjpeg-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN ln -sf /usr/bin/python3 /usr/bin/python

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8084
CMD ["python3", "main.py"]