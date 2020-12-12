shipping_system

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
docker-compose run web python manage.py migrate --rm
```

# load fixture
```
docker-compose run web /bin/bash --rm
python manage.py loaddata ./curation/fixtures/category.json
python manage.py loaddata ./curation/fixtures/menu.json


```

