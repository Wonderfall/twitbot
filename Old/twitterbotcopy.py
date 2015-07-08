#!/usr/bin/env python3

### REQUIRED IMPORT
import time, sys, psutil, subprocess, shutil, os, random
from datetime import timedelta, datetime
from apscheduler.schedulers.background import BackgroundScheduler
from twython import Twython, TwythonError, TwythonStreamer

#### Twitter Credentials & accounts
API_KEY             = 'Consumer Key (API Key)'
API_SECRET          = 'Consumer Secret (API Secret)'
ACCESS_TOKEN        = 'Access Token'
ACCESS_TOKEN_SECRET = 'Access Token Secret'
BOT, MASTER         = 'bot', 'utilisateur'
api                 = Twython(API_KEY,API_SECRET,ACCESS_TOKEN,ACCESS_TOKEN_SECRET)

#### Path variables
with open('twitterbot.log', 'w+'): pass
LOG                = 'twitterbot.log'
OSSEC_LOG          = '/var/ossec/logs/alerts/alerts.log'

#### Scheduler : daily tweets & log remover
def delete_tweets():
    user_timeline = api.get_user_timeline(screen_name=BOT, count=100)
    for tweets in user_timeline:
        api.destroy_status(id=tweets['id_str'])

def delete_log():
    open(LOG, 'w').close()

def check_intrusions(level=10):
    f = open(OSSEC_LOG).read()
    for i in range(7):
        if ('(level ' + str(level+i) + ')') in f:
            tweet_random('@' + MASTER + ' Something is going wrong!')
            return True
            break

def check_updates():
    subprocess.call(['aptitude', 'update'])
    f = subprocess.check_output(['aptitude', 'upgrade', '-s', '-y']).decode('utf-8')
    if '0 packages upgraded' not in f:
        tweet_random('@' + MASTER + ' Uptates are available.')
        return True

scheduler = BackgroundScheduler()
scheduler.add_job(delete_tweets, 'interval', hours=24)
scheduler.add_job(delete_log, 'interval', hours=24)
scheduler.add_job(check_intrusions, 'interval', hours=1)
scheduler.add_job(check_updates, 'interval', hours=1)
scheduler.start() # Comment it if you don't want to use it

#### Stream filter
FOLLOW = str(int(api.show_user(screen_name=MASTER)['id_str']))
TERMS = '@' + BOT

#### Functions
def append_log(to_write):
    with open(LOG, 'a') as f:
        f.write('At ' + str(datetime.now()) + ' : ' + to_write + '\n')

def tweet_random(output=None):
    if output == None: output = 'How can I help you?'
    api.update_status(status=output + '\n' + '[' + str(random.randint(1,9999)) + ']')

def give_uptime():
    with open('/proc/uptime', 'r') as f:
        uptime_seconds = int(float(f.readline().split()[0]))
        tweet_random("I've been up for " + str(timedelta(seconds=uptime_seconds)))

def give_systats():
    tweet_random("CPU load : " + str(psutil.cpu_percent(interval=2)) + " %" + '\n' +
                 "RAM usage : " + str(psutil.virtual_memory().percent) + " %")

def speedtest():
    tweet_random(subprocess.check_output(["speedtest-cli", "--simple"]).decode('utf-8')[:-1])

def check_system():
    if (check_intrusions() != True) and (check_updates() != True):
        tweet_random("Everything is OK.")
    elif check_updates(): pass

#### Associated words & answer function
options = {
    'toast'         : tweet_random,
    'uptime'        : give_uptime,
    'stats'         : give_systats,
    'speedtest'     : speedtest,
    'checksys'      : check_system
}

words_options = options.keys()

def answer(tweet):
    splited_tweet = tweet.split()
    for i in range(len(splited_tweet)):
        if splited_tweet[i] in words_options:
            options[splited_tweet[i]]()
            break

#### Streamer
class TweetStreamer(TwythonStreamer):
    def on_success(self, data):
        if ('text' in data) and (TERMS in data['text']):
            append_log('tweet from ' + MASTER + ' to ' + BOT + ' received.')
            answer(data['text'])

    def on_error(self, status_code, data):
        self.disconnect()

stream = TweetStreamer(API_KEY,API_SECRET,ACCESS_TOKEN,ACCESS_TOKEN_SECRET)

try:
    stream.statuses.filter(follow=FOLLOW)
except TwythonError as e:
    append_log(str(e))