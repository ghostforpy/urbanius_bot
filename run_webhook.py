import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dtb.settings')
django.setup()

from tgbot.handlers.dispatcher import run_webhook

if __name__ == "__main__":
    run_webhook()