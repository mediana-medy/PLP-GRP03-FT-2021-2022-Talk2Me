import random
import time
import re
import telepot
from telepot.loop import MessageLoop
from config import *
from conversation.conv_interact import *
from risk_inference import get_risk
from condition_inference import condition_classify
from Condition_inference_BERT import predict_sentiment

history = {'dialog': [], }
USER_END_PHRASES = [
    "bye",
    "thanks",
    "thank you",
    "alright",
    "okay",
    "ok"
]

def request_handler(msg):  # directly monitor telegram
    (msg_type, chat_type, chat_id) = telepot.glance(msg)
    print(msg_type, chat_type, chat_id, msg["from"]["username"], msg["text"])
    start = 0

    if msg_type == "text" and re.search(START_REGEX, str(msg['text'].lower())):
        start = 1
        username = msg['from']['username']
        start_msg = random.choice(GREETINGS) + username + random.choice(WELCOME_MSG)
        bot.sendMessage(chat_id, str(start_msg))

    if start == 0 and msg_type == 'text':
        user_utterances = str(msg['text'])
        if re.search(HOTLINE_REGEX, user_utterances.lower()):
            for resources in HOTLINES_LIST:
                bot.sendMessage(chat_id, resources)
        elif user_utterances.lower() in USER_END_PHRASES:
            end_msg = "AI: " + random.choice(END_MSG)
            print(end_msg)
            bot.sendMessage(chat_id, str(end_msg))
            # get the high/low risk score of the user (0 to 1) based on the dialogue history
            risk_score, combined_user_texts = get_risk(history)
            print("Risk Score:", risk_score)
            # get the final condition type ['emotional','family','friendship','others','relationship','school','work']
            condition_type = condition_classify(combined_user_texts)
            # condition_type = predict_sentiment(combined_user_texts)  # Using BERT
            print("Condition Type:", condition_type)
            # if user risk_score is above threshold, send additional help links
            if risk_score > 0.5:
                print(str(PROFESSIONAL_HELP_MSG[0]))
                bot.sendMessage(chat_id, str(PROFESSIONAL_HELP_MSG[0]))

            #TO BE UPDATED WITH FEEDBACK
            # bot.sendMessage(chat_id, str("Feedback: "))
            # fb_resp = bot.getUpdates()
            fb_resp=""
            with open("insight_data.txt", "a") as file_object:
                # Append 'hello' at the end of file
                data_user = str(msg['from']['username']) + ", " \
                            + str(condition_type[0]) + ", " + str(risk_score[0]) + ", " + fb_resp + "\n"
                file_object.write(data_user)

        elif re.search(CHAT_REGEX, user_utterances.lower()):
            response = chat_conv(user_utterances, history)
            print(response)
            bot.sendMessage(chat_id, response)
        else:
            response = chat_conv(user_utterances, history)
            print(response)
            bot.sendMessage(chat_id, response)

        print(history)

bot = telepot.Bot(BOT_TOKEN)
MessageLoop(bot, request_handler).run_as_thread()

while 1:
    time.sleep(5)
