#!/bin/sh
sed -i -e "s/<API_KEY>/${API_KEY}/g" \
       -e "s/<API_SECRET>/${API_SECRET}/g" \
       -e "s/<ACCESS_TOKEN>/${ACCESS_TOKEN}/g" \
       -e "s/<ACCESS_TOKEN_SECRET>/${ACCESS_TOKEN_SECRET}/g" \
       -e "s/<BOT>/${BOT}/g" -e "s/<MASTER>/${MASTER}/g" \
       /opt/twitbot.py

chown -R $UID:$GID /opt/twitbot.py /twitbot
su-exec $UID:$GID python3 /opt/twitbot.py
