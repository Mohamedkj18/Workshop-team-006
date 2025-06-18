FROM python:3.10

ENV NLTK_DATA=/usr/share/nltk_data

WORKDIR /app

# 🔧 Install netcat for wait-for-db.sh
RUN apt-get update && apt-get install -y netcat-openbsd && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt

RUN rm -rf /usr/share/nltk_data/* && \
    python -m nltk.downloader -d /usr/share/nltk_data punkt averaged_perceptron_tagger

COPY . .
RUN chmod +x wait-for-db.sh

CMD ["./wait-for-db.sh"]
