#!/usr/bin/env python3

### REQUIRED IMPORT
import time, sys, psutil, subprocess, shutil, os, random
from datetime import timedelta, datetime
from apscheduler.schedulers.background import BackgroundScheduler
from twython import Twython, TwythonError, TwythonStreamer

#### Twitter Credentials & accounts
API_KEY             = 'foobar'
API_SECRET          = 'foobar'
ACCESS_TOKEN        = 'foobar'
ACCESS_TOKEN_SECRET = 'foobar'
BOT, MASTER         = 'foobar', 'foobar'
api                 = Twython(API_KEY,API_SECRET,ACCESS_TOKEN,ACCESS_TOKEN_SECRET)

#### Path variables
LOG                = 'foobar'
TORRENTS_COMPLETED = 'foobar'
TORRENTS_PROGRESS  = 'foobar'
OWNCLOUD_TORRENTS  = 'foobar'
RKHUNTER_LOG       = 'foobar'

#### Scheduler : daily tweets & log remover
def delete_tweets():
    user_timeline = api.get_user_timeline(screen_name=BOT, count=100)
    for tweets in user_timeline:
        api.destroy_status(id=tweets['id_str'])

def delete_log():
    f = open(LOG, 'w')
    f.close()

scheduler = BackgroundScheduler()
scheduler.add_job(delete_tweets, 'interval', hours=24)
scheduler.add_job(delete_log, 'interval', hours=24)
scheduler.start() # Comment it if you don't want to use it

#### Stream filter
FOLLOW = str(int(api.show_user(screen_name=MASTER)['id_str']))
TERMS = '@' + BOT

#### Functions
def append_log(to_write):
    with open(LOG, 'a') as f:
        f.write('At ' + str(datetime.now()) + ' : ' + to_write + '\n')

def tweet_random(output=None):
    if output == None: output = 'Roah. Tell me something understable.'
    api.update_status(status=output + '\n' + '#' + str(random.randint(1,9999)))

def give_uptime():
    with open('/proc/uptime', 'r') as f:
        uptime_seconds = int(float(f.readline().split()[0]))
        tweet_random("I'm up since " + str(timedelta(seconds=uptime_seconds)))

def give_cpuload():
    tweet_random("CPU load : " + str(psutil.cpu_percent(interval=2)) + " %")

def give_RAMusage():
    tweet_random("RAM usage : " + str(psutil.phymem_usage().percent) + " %")

def speedtest():
    tweet_random(subprocess.check_output(["speedtest-cli", "--simple"]).decode('utf-8')[:-1])

def check_malwares():
    f = open(RKHUNTER_LOG).read()
    if ('rootkits: 0' in f) and ('files: 0' in f):
        tweet_random("No rootkits, no supect files. Nothing to worry about.")
    else:
        tweet_random("A son of bitch is annoying me. Check me as soon as you can.")

def move_torrents():
    for item in os.listdir(TORRENTS_COMPLETED):
        s = os.path.join(TORRENTS_COMPLETED, item)
        d = os.path.join(OWNCLOUD_TORRENTS, item)
        if os.path.exists(d):
            try:
                shutil.rmtree(d)
            except Exception as e:
                os.unlink(d)
        if os.path.isdir(s):
            shutil.copytree(s, d, False, None)
        else:
            shutil.copy2(s, d)
    shutil.rmtree(TORRENTS_COMPLETED)
    tweet_random('Torrent(s) moved, sir, synchronizing to your cloud folder.')

def downloading_torrents():
    tweet_random(str(len(os.listdir(TORRENTS_PROGRESS))) + ' torrent(s) are downloading, sir.')

#### Associated words & answer function
options = {
    'toast'         : tweet_random,
    'uptime'        : give_uptime,
    'CPU'           : give_cpuload,
    'RAM'           : give_RAMusage,
    'speedtest'     : speedtest,
    'malwares'      : check_malwares,
    'moveTorrents'  : move_torrents,
    'checkTorrents' : downloading_torrents
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