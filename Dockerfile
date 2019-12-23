FROM tiangolo/uwsgi-nginx-flask:python3.7
RUN apt-get update --no-install-recommends && \
    apt-get install -y supervisor build-essential libpq-dev gcc cmake
RUN pip install --no-cache-dir --disable-pip-version-check face_recognition redis cachetools

COPY app.py /app/app.py
COPY kface.py /app/kface.py
COPY uwsgi.ini /app/uwsgi.ini
COPY uwsgi-nginx-entrypoint.sh /uwsgi-nginx-entrypoint.sh
COPY entrypoint.sh /entrypoint.sh
COPY confd_nginx.conf /app/confd_nginx.conf
COPY templates /app/templates
RUN mkdir /uploads /known /app/match
COPY match/jquery.min.js /app/match

ENV UPLOAD_FOLDER /uploads
ENV KNOWNS_FOLDER /known
ENV MATCH_FOLDER /app/match
ENV REDIS 127.0.0.1


EXPOSE 80
