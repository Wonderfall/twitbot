#!/usr/bin/env python3
# -*- coding: utf-8 -*-

### Requirements
import time, sys, psutil, subprocess, shutil, os, random
from datetime import timedelta, datetime
from apscheduler.schedulers.background import BackgroundScheduler
from twython import Twython, TwythonError, TwythonStreamer

#### Twitter Credentials & accounts
API_KEY             = "<API_KEY>"
API_SECRET          = "<API_SECRET>"
ACCESS_TOKEN        = "<ACCESS_TOKEN>"
ACCESS_TOKEN_SECRET = "<ACCESS_TOKEN_SECRET>"
BOT, MASTER         = "<BOT>", "<MASTER>"
api                 = Twython(API_KEY,API_SECRET,ACCESS_TOKEN,ACCESS_TOKEN_SECRET)

#### Path variables
LOG         = "/twitbot/twitter.log"
DICTIONARY  = "/twitbot/dico.txt"

#### Functions
def append_log(event):
    with open(LOG, 'a') as f:
        f.write("At " + str(datetime.now()) + " : " + event + '\n')

def clean_log():
    if os.path.getsize(LOG)/(1024*1024) > 10:
        with open(LOG, 'w+'): pass

def rand_tweet(id='', output="Meow."):
    append_log("triggered " + str(rand_tweet))

    if id != '':
        output = '@' + MASTER + ' ' + output
        api.update_status(status=output + '\n' + '[' + str(random.randint(1000,9999)) + ']', in_reply_to_status_id=id)
    else:
        api.update_status(status=output + '\n' + '[' + str(random.randint(1000,9999)) + ']')

def give_uptime(id=''):
    append_log("triggered " + str(give_uptime))

    with open('/proc/uptime', 'r') as f:
        uptime_seconds = int(float(f.readline().split()[0]))

    rand_tweet(id, "Je suis debout depuis " +
               str(timedelta(seconds=uptime_seconds).days) + " jour(s), " +
               str(timedelta(seconds=uptime_seconds).seconds // 3600) + " heure(s) et " +
               str(timedelta(seconds=uptime_seconds).seconds // 60 % 60) + " minute(s). " +
               "Dernier dodo le " + str(datetime.fromtimestamp(psutil.boot_time()).strftime("%d/%m/%Y")) + ".")

def give_cpu_temp(id=''):
    append_log("triggered " + str(give_cpu_temp))

    with open('/sys/class/thermal/thermal_zone2/temp', 'r') as f:
        temperature = int(f.read())*(10**-3)

    temp_qualitative = "J'ai un peu chaud... poke @" + MASTER if temperature >= 60 else "Tout va bien."
    rand_tweet(id, "Ma température CPU est de " + str(temperature) + "°C. " + temp_qualitative)

def give_systats(id=''):
    append_log("triggered " + str(give_systats))
    cpu_load = psutil.cpu_percent(interval=2)
    ram_usage = psutil.virtual_memory().percent

    if (cpu_load >= 80) or (ram_usage >= 70):
        stats_qualitative = "J'en ai du boulot... poke @" + MASTER
    elif (cpu_load <= 4) and (ram_usage <= 20):
        stats_qualitative = "Journée de rêve..."
    else:
        stats_qualitative = "Voilà !"

    rand_tweet(id, "Je suis à " + str(cpu_load) + "% de mes capacités et j'utilise " +
               str(ram_usage) + "% de ma mémoire vive. " + stats_qualitative)

def speedtest(id=''):
    append_log("triggered " + str(speedtest))
    rand_tweet(id, subprocess.check_output(["speedtest-cli", "--simple"]).decode('utf-8')[:-1] +
               '\n' + "Rapide non ?")

def pick_a_quote(id=''):
    append_log("triggered " + str(pick_a_quote))
    rand_tweet(id, random.choice(open(DICTIONARY, 'r', encoding="utf-8").readlines())[:-1])

#### Scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(pick_a_quote, 'interval', hours=6)
scheduler.add_job(give_uptime, 'cron', day_of_week='wed', hour='20')
scheduler.add_job(give_cpu_temp, 'cron', day_of_week='tue-sat', hour='20')
scheduler.add_job(give_systats, 'cron', day_of_week='mon-wed-sun', hour='21')
scheduler.add_job(speedtest, 'cron', day_of_week='thu', hour='19')
scheduler.add_job(clean_log, 'cron', day_of_week='sun', hour='23')
scheduler.start()

#### Answer function
commands = {
    "toast"         : rand_tweet,
    "salut"         : rand_tweet,
    "hello"         : rand_tweet,
    "uptime"        : give_uptime,
    "debout"        : give_uptime,
    "stats"         : give_systats,
    "statistiques"  : give_systats,
    "charge"        : give_systats,
    "travail"       : give_systats,
    "temp"          : give_cpu_temp,
    "temps"         : give_cpu_temp,
    "température"   : give_cpu_temp,
    "températures"  : give_cpu_temp,
    "chaud"         : give_cpu_temp,
    "froid"         : give_cpu_temp,
    "speedtest"     : speedtest,
    "vitesse"       : speedtest,
    "débit"         : speedtest,
    "quote"         : pick_a_quote,
    "citation"      : pick_a_quote,
    "rire"          : pick_a_quote,
    "blague"        : pick_a_quote
}

keys = list(commands.keys())

def answer(tweet, id):
    for i in range(len(keys)):
        if keys[i] in tweet:
            append_log("match with " + str(commands[keys[i]]))
            commands[keys[i]](id)
            break
    else: rand_tweet(id, "What? Je crains ne pas comprendre !")

#### Streamer
class TweetStreamer(TwythonStreamer):
    def on_success(self, data):
        if ('text' in data) and ('@' + BOT in data['text']):
            append_log("tweet from " + MASTER + " to " + BOT + " received.")
            append_log("tweet id is " + data['id_str'])
            answer(data['text'].lower(), data['id_str'])
            append_log(BOT + " answered.")

    def on_error(self, status_code, data):
        append_log("had to disconnect because of error " + str(status_code))
        self.disconnect()

stream = TweetStreamer(API_KEY,API_SECRET,ACCESS_TOKEN,ACCESS_TOKEN_SECRET)
append_log("twitbot initialized.")

try:
    stream.statuses.filter(follow=str(int(api.show_user(screen_name=MASTER)['id_str'])))
except TwythonError as e:
    append_log(str(e))
