web: python manage.py migrate --noinput && python manage.py load_amont && gunicorn config.wsgi --bind 0.0.0.0:$PORT --workers 2
