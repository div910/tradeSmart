FROM centos:7
LABEL maintainer="Trade Smart Team"

RUN \
 yum install -y epel-release && \
 yum install -y wget \
                git \
                which \
                make \
                python-setuptools \
                python-pip \
                python-dev \
                zlib-devel \
                openssl-devel \
                mysql-devel \
                python-devel \
                gcc-c++ \
                snappy-devel \
                gcc \
                postgresql \
                postgresql-devel \
                sqlite-devel \
                expat-devel \
                bzip2-devel \
                libffi-devel \
                zlib-devel \
                libxslt-devel \
                libxml2-devel \
                python-argparse \
                xmlsec1-devel \
                xmlsec1-openssl-devel \
                libtool-ltdl-devel && \
 yum install -y nginx && \
 yum install -y screen && \
 pip install supervisor && \
 mkdir -p /var/log/supervisor /etc/supervisord.d /logs /opt/logs /etc/newrelic && \
 yum clean all

EXPOSE 80
EXPOSE 8000

RUN \
 cd /opt && \
 wget https://www.python.org/ftp/python/3.10.6/Python-3.10.6.tgz  && \
 tar xzf Python-3.10.6.tgz && \
 cd /opt/Python-3.10.6 && \
 ./configure --enable-shared --with-system-ffi --with-system-expat --enable-unicode=ucs4 --prefix=/usr/local/python3.8 LDFLAGS="-L/usr/local/python3.10/lib -Wl,--rpath=/usr/local/python3.10/lib"  && \
 make && \
 make altinstall && \
 rm -f /etc/localtime && \
 ln -s /usr/share/zoneinfo/Asia/Kolkata /etc/localtime && \
 rm -Rf Python-3.10.6.tgz /opt/Python-3.10.6

WORKDIR /usr/local/trade_smart/

COPY config/supervisord /etc/rc.d/init.d/supervisord
ADD  config/services/* /etc/supervisord.d/
COPY config/nginx/nginx.conf /etc/nginx/nginx.conf
COPY config/uwsgi/uwsgi_params /etc/nginx/uwsgi_params
COPY config/uwsgi/uwsgi_params /etc/nginx/conf.d/uwsgi_params
COPY config/uwsgi/trade_smart_uwsgi.ini /etc/trade_smart_uwsgi.ini
COPY config/nginx/trade_smart.conf /etc/nginx/conf.d/trade_smart.conf
COPY config/pip/requirements.txt /etc/pip/requirements.txt

RUN /usr/local/python3.10/bin/pip3.10 install -r /etc/pip/requirements.txt

COPY ./ /usr/local/trade_smart

RUN \
#   /usr/local/python3.10/bin/python3.10  /usr/local/creditas/sandesh/sandesh_proj/manage.py collectstatic && \
  chmod 755 /etc/rc.d/init.d/supervisord

#CMD ["/usr/bin/supervisord", "-n", "-c", "/etc/supervisord.d/trade_smart_web_service.conf"]