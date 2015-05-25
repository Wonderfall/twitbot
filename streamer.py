#!/usr/bin/env python

# REQUIRED
import time
import sys
import psutil
import subprocess
from twython import TwythonStreamer
from twython import Twython
from datetime import timedelta

# Twitte Authentification
apiKey = 'foobar'
apiSecret = 'foobar'
accessToken = 'foobar'
accessTokenSecret = 'foobar'
api = Twython(apiKey,apiSecret,accessToken,accessTokenSecret)

# Stream filter
TERMS = 'foobar'
FOLLOW = 'foobar'

# Functions
def giveUptime() :
    with open('/proc/uptime', 'r') as f:
        uptime_seconds = float(f.readline().split()[0])
        uptime_string = "Uptime : " + str(timedelta(seconds = uptime_seconds))
    return uptime_string

def giveCPU() :
    cpuLoad = "CPU load : " + str(psutil.cpu_percent(interval=1)) + " %"
    return cpuLoad

def giveRAM() :
    RAMusage = "RAM usage : " + str(psutil.phymem_usage().percent) + " %"
    return RAMusage

def speedtest() :
    output = subprocess.check_output(["speedtest-cli", "--simple"])
    return output

def answer(tweet) :
    if 'toast' in tweet:
        api.update_status(status="Tell me what I've to do...")
    elif 'uptime' in tweet:
        api.update_status(status=giveUptime())
    elif 'CPUload' in tweet:
        api.update_status(status=giveCPU())
    elif 'RAMusage' in tweet:
        api.update_status(status=giveRAM())
    elif 'speedtest' in tweet:
        api.update_status(status=speedtest())
    else :
        api.update_status(status="I'm afraid I don't understand...")

# Streamer
class TweetStreamer(TwythonStreamer):
    def on_success(self, data):
        if 'text' in data:
            print data['text'].encode('utf-8')
            answer(data['text'])

    def on_error(self, status_code, data):
        print status_code
        self.disconnect()

stream = TweetStreamer(apiKey,apiSecret,accessToken,accessTokenSecret)
stream.statuses.filter(tracks=TERMS, follow=FOLLOW)