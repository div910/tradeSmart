# Base image
FROM python:3.11.4-bookworm

# Install system dependencies
RUN apt-get update &&  \
    apt-get install -y build-essential nginx redis-server && \
    /usr/local/bin/pip3 install supervisor && \
    mkdir -p /var/log/supervisor /etc/supervisord.d /logs /opt/logs


# Expose ports
EXPOSE 80
EXPOSE 5555

WORKDIR /usr/local/trade_smart/

COPY config/supervisord /etc/rc.d/init.d/supervisord
ADD  config/services/* /etc/supervisord.d/
COPY config/nginx/nginx.conf /etc/nginx/nginx.conf
COPY config/nginx/uwsgi_params /etc/nginx/uwsgi_params
COPY config/nginx/uwsgi_params /etc/nginx/conf.d/uwsgi_params
COPY config/uwsgi/trade_smart_uwsgi.ini /etc/trade_smart_uwsgi.ini
COPY config/uwsgi/trade_smart.conf /etc/nginx/conf.d/trade_smart.conf

COPY config/pip/requirements.txt /etc/pip/requirements.txt
RUN /usr/local/bin/pip3 install -r /etc/pip/requirements.txt

COPY ./ /usr/local/trade_smart
