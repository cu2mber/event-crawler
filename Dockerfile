FROM eclipse-temurin:21-jdk

LABEL authors="yeong"

# Java 환경 위에 Python 설치
RUN apt-get update && \
    apt-get install -y --no-install-recommends python3.10 python3-pip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 파이썬 명령어를 'python'으로 사용할 수 있도록 심볼릭 링크 생성 (선택 사항)
RUN ln -sf /usr/bin/python3.10 /usr/bin/python

WORKDIR /app
COPY requirements.txt .
# pip3 대신 일반 python 환경에서 실행되도록 pip3 대신 pip 사용
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8084
# CMD 명령은 파이썬을 사용합니다.
CMD ["python", "main.py"]