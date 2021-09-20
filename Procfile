release: python manage.py migrate
web: gunicorn FakeCSV.wsgi --log-file -
worker: celery -A FakeCSV worker --loglevel=info