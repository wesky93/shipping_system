shipping_system

[http://django.handson.today:8000](http://django.handson.today:8000)

# init
```
docker-compose build
docker-compose up -d
docker-compose run web python manage.py migrate --rm

docker-compose run web /bin/bash --rm
python manage.py createsuperuser
```

# migrate
```
docker-compose run --rm web python manage.py migrate 
```

# load fixture
```
docker-compose run --rm web python manage.py loaddata ./curation/fixtures/category.json

docker-compose run --rm web python manage.py loaddata ./curation/fixtures/menu.json


```

