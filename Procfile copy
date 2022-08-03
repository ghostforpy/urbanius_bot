release: python manage.py migrate --noinput
web: gunicorn --bind :$PORT --workers 1 --worker-class uvicorn.workers.UvicornWorker dtb.asgi:application