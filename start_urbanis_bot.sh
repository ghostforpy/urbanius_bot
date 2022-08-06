#!/bin/sh
docker stop urban_web
docker stop urban_bot
docker rm urban_web
docker rm urban_bot
docker pull obrubov/urbaniusbot_web:latest
sleep 5
docker run -v /home/vitaly/bot_media:/media --name urban_web -t -d -p 8001:8001 obrubov/urbaniusbot_web
docker pull obrubov/urbaniusbot_bot:latest
sleep 5
docker run -v /home/vitaly/bot_media:/media --name urban_bot -t -d obrubov/urbaniusbot_bot

