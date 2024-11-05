FROM python

RUN useradd -m app
RUN chsh -s /bin/bash
WORKDIR /home/app/src

COPY requirements.txt .
RUN ["pip", "install", "--no-cache-dir", "-r", "requirements.txt"]
ENV FLASK_APP=alkhalideen.py