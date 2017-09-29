FROM python:3
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN apt-get update
RUN apt-get install -y gettext
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN python manage.py migrate
RUN python manage.py compilemessages
