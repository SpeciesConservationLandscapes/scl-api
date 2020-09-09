FROM python:3.7-slim-buster
LABEL maintainer="<sysadmin@datamermaid.org>"

RUN apt-get install -y --no-install-recommends cron

ADD ./requirements.txt requirements.txt
RUN pip install --upgrade -r requirements.txt
RUN rm requirements.txt

RUN apt-get update && apt-get install -y --no-install-recommends \
    gnupg \
    build-essential \
    apt-transport-https \
    ca-certificates \
    python3-dev \
    wget \
    curl \
    vim \
    less \
    nano \
    supervisor \
    nginx \
    gunicorn \
    postgis \
    gdal-bin \
    python-gdal

RUN echo 'deb http://apt.postgresql.org/pub/repos/apt/ stretch-pgdg main' >  /etc/apt/sources.list.d/pgdg.list
RUN wget --quiet -O - https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN wget --quiet -O - https://packages.microsoft.com/config/debian/9/prod.list > /etc/apt/sources.list.d/mssql-release.list
RUN wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -
RUN apt-get update
RUN ACCEPT_EULA=Y apt-get install -y --no-install-recommends \
    postgresql-client-11 \
    msodbcsql17

ADD ./odbc.ini /etc/odbc.ini

RUN pip install --upgrade pip
ADD ./requirements.txt ./requirements.txt
RUN pip install --upgrade -r ./requirements.txt
RUN rm ./requirements.txt

RUN groupadd webapps
RUN useradd webapp -G webapps
RUN mkdir -p /var/log/webapp/ && chown -R webapp /var/log/webapp/ && chmod -R u+rX /var/log/webapp/
RUN mkdir -p /var/run/webapp/ && chown -R webapp /var/run/webapp/ && chmod -R u+rX /var/run/webapp/
ADD ./config/gunicorn.conf /

RUN rm /etc/nginx/sites-enabled/default && rm /etc/nginx/sites-available/default
ADD ./config/webapp.nginxconf /etc/nginx/sites-enabled/

RUN mkdir -p /var/log/supervisor
ADD ./config/supervisor_conf.d/nginx.conf /etc/supervisor/conf.d/
ADD ./config/supervisor_conf.d/webapp.conf /etc/supervisor/conf.d/

WORKDIR /var/projects/webapp
ADD ./src .

COPY ./deploy/webapp.nginxconf /etc/nginx/sites-enabled/webapp.nginxconf

EXPOSE 8181 80 443
CMD ["supervisord", "-n", "-c", "/etc/supervisor/supervisord.conf"]
RUN (crontab -l ; echo "5 1,13 * * * /usr/bin/supervisorctl restart webapp") | crontab -
