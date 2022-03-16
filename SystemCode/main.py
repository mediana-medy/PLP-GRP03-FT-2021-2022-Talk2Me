import random
import time
import re
import telepot
from telepot.loop import MessageLoop
from myfunc_utils import *
from config import *
from conversation.conv_interact import *

history = {'dialog': [], }

def request_handler(msg):  # directly monitor telegram
    (msg_type, chat_type, chat_id) = telepot.glance(msg)
    print(msg_type, chat_type, chat_id, msg["from"]["username"], msg["text"])
    start = 0

    if msg_type == "text" and re.search(START_REGEX, str(msg['text'].lower())):
        start = 1
        username = msg['from']['username']
        start_msg = GREETINGS[random.randint(0, 2)] + username + WELCOME_MSG[random.randint(0, 2)]
        bot.sendMessage(chat_id, str(start_msg))

    if start == 0 and msg_type == 'text':
        user_utterances = str(msg['text'])

        if re.search(HOTLINE_REGEX, user_utterances.lower()):
            response = "HOTLINE response to " + user_utterances + hotline_func(user_utterances)
            print(user_utterances, response)
            bot.sendMessage(chat_id, response)
        elif re.search(CHAT_REGEX, user_utterances.lower()):
            response = chat_conv(user_utterances, history)
            print(response)
            bot.sendMessage(chat_id, response)
        else:
            response = chat_conv(user_utterances, history)
            print(response)
            bot.sendMessage(chat_id, response)
        print(history)
        # else:
        #     response = "Response: " + user_utterances
        #     print(user_utterances, response)
        #     bot.sendMessage(chat_id, response)

bot = telepot.Bot(BOT_TOKEN)
MessageLoop(bot, request_handler).run_as_thread()

while 1:
    time.sleep(5)
