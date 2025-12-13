FROM openjdk:21-slim

LABEL authors="yeong"

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3 python3-pip \
        wget \
        gnupg \
        libnss3 libxss1 libgbm-dev fonts-liberation libasound2t64 libatk1.0-0 libgtk-3-0 libappindicator3-1 \
        xdg-utils libwoff1 fonts-dejavu libgdk-pixbuf2.0-0 libharfbuzz-icu0 libcurl4 libjpeg-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /etc/apt/keyrings/google-archive-keyring.gpg

RUN echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/google-archive-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list

RUN apt-get update && \
    apt-get install -y google-chrome-stable && \
    ln -s /usr/bin/google-chrome /usr/bin/chromium-browser && \
    ln -s /usr/bin/google-chrome /usr/bin/chromium && \
    ln -s /usr/bin/google-chrome /usr/bin/chromedriver


RUN ln -sf /usr/bin/python3 /usr/bin/python

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --break-system-packages

COPY . .

EXPOSE 8084
CMD ["python3", "main.py"]