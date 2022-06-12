'''
Core file in which the bot is run.
Runs in two threads
1. Ban thread
2. Updater thread
'''


import os
import schedule
import logging
from threading import Thread
from time import sleep
from global_init import API_TOKEN
from tg import ban, updater

logging.basicConfig(
    format='%(asctime)s - %(filename)s - %(funcName)s (%(lineno)d) - %(levelname)s - %(message)s', level=logging.INFO)


############################## Threading ########################################

schedule.every().hour.do(ban)


def scheduler():
    while True:
        schedule.run_pending()
        sleep(10)


scheduler_thread = Thread(target=scheduler)
scheduler_thread.start()

port = int(os.getenv('PORT', 4200))  # Heroku port

updater.start_webhook(listen="0.0.0.0",
                      port=port,
                      url_path=API_TOKEN,
                      webhook_url=f'https://fundstrat-subscription-bot.herokuapp.com/{API_TOKEN}')

updater.idle()
