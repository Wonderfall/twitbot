#!/usr/bin/env python

# REQUIRED IMPORTS
import time
import sys
import psutil
import subprocess
import shutil
import os
import random
from datetime import timedelta
from apscheduler.scheduler import Scheduler # Must be apscheduler 2.1.2 !
from twython import Twython, TwythonError, TwythonStreamer

#### Twitter Credentials & accounts
apiKey = 'foobar'
apiSecret = 'foobar'
accessToken = 'foobar'
accessTokenSecret = 'foobar'
bot, master = 'foobar', 'foobar'
api = Twython(apiKey,apiSecret,accessToken,accessTokenSecret)

#### Path variables
log = 'foobar'
torrentsCompleted = 'foobar'
torrentsProgress = 'foobar'
owncloudTorrents = 'foobar'
rkhunterLog = 'foobar'

#### Scheduler : daily tweets remover
sched = Scheduler()

@sched.interval_schedule(hours=24)
def delete_tweets():
    user_timeline = api.get_user_timeline(screen_name=bot, count=100)
    for tweets in user_timeline:
        api.destroy_status(id=tweets['id_str'])
def delete_log():
    f = open(log, 'w')
    f.close()

sched.start() # Comment it if you don't want to use it

#### Stream filter
FOLLOW = str(int(api.show_user(screen_name=master))
TERMS = '@' + bot

#### Functions
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

def checkMalwares() :
    output1 = subprocess.check_output(["grep", "Possible", rkhunterLog])
    output2 = subprocess.check_output(["grep", "Suspect", rkhunterLog])
    if (output1[30] == '0') and (output2[26] == '0') :
        output = "No rootkits, no supect files. Nothing to worry about."
    else :
        output = "A son of bitch is annoying me. Check me as soon as you can."
    return output

def movetree(src, dst, deleteSrc, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.exists(d):
            try:
                shutil.rmtree(d)
            except Exception as e:
                os.unlink(d)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)
    if deleteSrc == True :
        shutil.rmtree(src)

def numberFiles(src):
    filesListed = len(os.listdir(src))
    return filesListed

def updateWithRandom(output):
    output = output + '\n' + '#' + str(random.randint(1,9999))
    api.update_status(status=output)

#### Answer function
def answer(tweet) :

    if 'toast' in tweet:
        updateWithRandom("Tell me what I've to do...")

    elif 'uptime' in tweet:
        api.update_status(status=giveUptime())

    elif ('CPU' in tweet) or ('load' in tweet):
        updateWithRandom(giveCPU())

    elif ('RAM' in tweet) or ('memory' in tweet):
        updateWithRandom(giveRAM())

    elif 'speedtest' in tweet:
        api.update_status(status=speedtest())

    elif ('malwares' in tweet) or ('rootkits' in tweet):
        updateWithRandom(checkMalwares())

    elif ('torrents' in tweet) and (('check' in tweet) or ('copy' in tweet) or ('move' in tweet) or ('clean' in tweet) or ('save' in tweet)) :

        if 'check' in tweet: 
            inProgress = numberFiles(torrentsProgress)
            checkedTorrents = ' ' + str(inProgress) + ' torrent(s) are in progress.'
            whatDone = ' checked '
        elif ('copy' in tweet) or ('save' in tweet):
            movetree(torrentsCompleted, owncloudTorrents, False)
            whatDone, checkedTorrents = ' copied ', ''
        elif ('move' in tweet) or ('clean' in tweet):
            movetree(torrentsCompleted, owncloudTorrents, True)
            whatDone, checkedTorrents = ' moved ', ''

        outputTorrents = 'Torrents have been' + whatDone + ', sir.' + checkedTorrents
        updateWithRandom(outputTorrents)

    else :
        updateWithRandom("I'm afraid I don't understand...")

#### Streamer
class TweetStreamer(TwythonStreamer):
    def on_success(self, data):
        if ('text' in data) and (TERMS in data['text']):
            f = open(log, 'a')
            infoLog = 'Received at ' + datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S') + ' : ' + data['text'] + '\n'
            f.write(infoLog)
            f.close()
            #print data['text'].encode('utf-8')
            answer(data['text'])

    def on_error(self, status_code, data):
        f = open(log, 'a')
        errorLog2 = 'Error at ' + datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S') + ' : ' + status_code + '\n'
        f.write(errorLog2)
        f.close()
        #print status_code
        self.disconnect()

stream = TweetStreamer(apiKey,apiSecret,accessToken,accessTokenSecret)

try :
    stream.statuses.filter(follow=FOLLOW)
except TwythonError as e :
    f = open(log, 'a')
    errorLog = 'Error at ' + datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S') + ' : ' + e
    f.write(errorLog)
    f.write('\n Valar Morghulis. \n \n \n')
    f.close()
    #print e