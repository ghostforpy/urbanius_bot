# import os
# import json
import logging
import requests
from django.conf import settings

#from tgcommands import available_commands
#import sys

logger = logging.getLogger(__name__)

#AVAILABLE_COMMANDS = available_commands.AVAILABLE_COMMANDS
# TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", False)
# WEBHOOK_URL = os.getenv("WEBHOOK_URL", False)

if not settings.DEBUG:
    logger.info("Set telegram webhook url {}".format(settings.TELEGRAM_WEBHOOK))
    # print('Set telegram webhook url')

    url = "https://api.telegram.org/bot{}/setWebhook?url={}".format(
        settings.TELEGRAM_TOKEN,
        settings.TELEGRAM_WEBHOOK
    )
    r = requests.post(url)
    json_response = r.json()
    logger.info(json_response)
    # print(json_response)

    # print('Set telegram bot commands')
    # url = 'https://api.telegram.org/bot{}/setMyCommands'.format(
    #     TELEGRAM_BOT_TOKEN
    # )
    # commands = json.dumps([
    #     {'command': i, 'description': AVAILABLE_COMMANDS[i]} for i in AVAILABLE_COMMANDS
    # ])
    # r = requests.post(url, data={'commands': commands})
    # json_response = r.json()
    # print(json_response)
exit()
