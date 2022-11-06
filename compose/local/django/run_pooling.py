import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dtb.config.local')
django.setup()

from tgbot.handlers.dispatcher import run_pooling

if __name__ == "__main__":
    run_pooling()