FROM python:3.8
ENV PYTHONUNBUFFERED 1
RUN pip install -U pip setuptools
WORKDIR /web
COPY . .

RUN pip install -r requirements-dev.txt
RUN pip install https://github.com/lukasvinclav/django-admin-numeric-filter/archive/master.zip
CMD python manage.py runserver 0:8000