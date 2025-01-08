FROM python:3.13-slim

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

RUN apt-get -y update && apt-get -y install libsystemd-dev gcc pkg-config && \
	pip3 install systemd-python && \
	apt-get -y remove libsystemd-dev gcc pkg-config && \
	apt-get -y autoremove && \
	rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1

COPY . /usr/src/app

CMD ["/usr/src/app/main.py"]
