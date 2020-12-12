FROM python:3.8
ENV PYTHONUNBUFFERED 1
RUN pip install -U pip setuptools
WORKDIR /web
COPY . .

RUN pip install -r requirements-dev.txt
RUN pip install -e git+https://github.com/lukasvinclav/django-admin-numeric-filter.git@9bd51fd9c9309b54c3a13f9a594775a014b2695e#egg=django-admin-numeric-filter

CMD python manage.py runserver 0:8000