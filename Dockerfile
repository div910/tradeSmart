# Base image
FROM python:3.11.4-bookworm

# Install system dependencies
RUN apt-get update &&  \
    apt-get install -y build-essential

# Expose ports
EXPOSE 80

RUN mkdir -p /logs /opt/logs

WORKDIR /usr/local/trade_smart/

COPY /config/pip/requirements.txt /etc/pip/requirements.txt
RUN /usr/local/bin/pip3 install -r /etc/pip/requirements.txt

COPY ./trade_smart_backend/ /usr/local/trade_smart
