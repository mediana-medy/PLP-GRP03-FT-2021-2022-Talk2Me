import random
import time
import re
import telepot
from telepot.loop import MessageLoop

from config import *


def reqHandler(msg):  # directly monitor telegram
    (msg_type, chat_type, chat_id) = telepot.glance(msg)
    # print(msg_type, chat_type, chat_id, msg)
    start = 0

    if msg_type == "text" and re.search(START_REGEX, str(msg['text'].lower())):
        start=1
        rdm = random.randint(0, 2)
        username = msg['from']['username']
        start_msg = GREETINGS[rdm] + username + WELCOME_MSG[rdm]
        bot.sendMessage(chat_id, str(start_msg))

    if start == 0 and msg_type == 'text':
        user_utterances = str(msg['text'])
        if re.search(CHAT_REGEX, user_utterances.lower()):
            response = "Robot response to " + user_utterances
            bot.sendMessage(chat_id, response)
        elif re.search(HOTLINE_REGEX, user_utterances.lower()):
            response = "Robot response to " + user_utterances
            bot.sendMessage(chat_id, response)

bot = telepot.Bot(BOT_TOKEN)
MessageLoop(bot, reqHandler).run_as_thread()


while 1:
    time.sleep(10)
