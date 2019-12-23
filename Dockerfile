FROM honeycrisp/docker:django-geo-api

RUN apt-get install -y --no-install-recommends cron

ADD ./requirements.txt requirements.txt
RUN pip install --upgrade -r requirements.txt
RUN rm requirements.txt

WORKDIR /var/projects/webapp
ADD ./src .

COPY ./deploy/webapp.nginxconf /etc/nginx/sites-enabled/webapp.nginxconf

EXPOSE 8181 80 443
CMD ["supervisord", "-n", "-c", "/etc/supervisor/supervisord.conf"]
RUN (crontab -l ; echo "5 1,13 * * * /usr/bin/supervisorctl restart webapp") | crontab -
