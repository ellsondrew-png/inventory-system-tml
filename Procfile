release: python manage.py migrate
web: gunicorn inventory_system.config.wsgi:application --bind 0.0.0.0:$PORT
