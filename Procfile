release: python manage.py migrate --no-input && python manage.py seed_products
web: gunicorn craftmarket.wsgi --workers 2 --timeout 60 --log-file -
