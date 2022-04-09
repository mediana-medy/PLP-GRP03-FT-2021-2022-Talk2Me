import time
import re
import telepot
from telepot.loop import MessageLoop
from config import *
from conversation.conv_interact import *
from SystemCode.condition.condition_inference import get_risk
from SystemCode.problem.problem_inference import get_problem

history = {}
feedback = {}
USER_END_PHRASES = [
    "bye",
    "quit",
    "end"
]

def request_handler(msg):  # directly monitor telegram
    (msg_type, chat_type, chat_id) = telepot.glance(msg)
    print(msg_type, chat_type, chat_id, msg["from"]["username"], msg["text"])
    start = 0
    username = msg['from']['username']
    if username not in history:
        history[username]=[]
        feedback[username]=False

    print(history)
    if msg_type == "text" and re.search(START_REGEX, str(msg['text'].lower())):
        start = 1
        start_msg = random.choice(GREETINGS) + username + random.choice(WELCOME_MSG)
        bot.sendMessage(chat_id, str(start_msg))

    if start == 0 and msg_type == 'text' and not feedback[username]:
        user_utterances = str(msg['text'])
        if re.search(HOTLINE_REGEX, user_utterances.lower()):
            for resources in HOTLINES_LIST:
                bot.sendMessage(chat_id, resources)
        elif user_utterances.lower() in USER_END_PHRASES:
            if not feedback[username]:
                feedback[username] = True
                bot.sendMessage(chat_id, str("Please rate TalkToMe bot from Bad (1) to excellent (10): "))
        elif re.search(CHAT_REGEX, user_utterances.lower()) and not feedback[username]:
            response = chat_conv(user_utterances, history, username)
            # response = chat_conv(user_utterances, history)
            print(response)
            bot.sendMessage(chat_id, response)
        else:
            response = chat_conv(user_utterances, history, username)
            # response = chat_conv(user_utterances, history)
            print(response)
            bot.sendMessage(chat_id, response)

    if feedback[username] and msg['text'].lower() not in USER_END_PHRASES:
        fb_resp = str(msg['text'])
        risk_score, combined_user_texts = get_risk(history, username)
        # get the final condition type ['emotional','family','friendship','others','relationship','school','work']
        problem_category = get_problem(combined_user_texts)
        # if user risk_score is above threshold, send additional help links
        if risk_score > 0.5:
            print(str(SCC_WEBSITES[0]))
            bot.sendMessage(chat_id, str(SCC_WEBSITES[0]))
        print("problem, riskscore: ", problem_category, risk_score[0], fb_resp)
        with open("insight_data.txt", "a") as file_object:
            # Append 'hello' at the end of file
            data_user = str(msg['from']['username']) + ", " \
                        + str(problem_category) + ", " + str(risk_score[0]) + ", " + str(fb_resp) + "\n"
            file_object.write(data_user)
        history.pop(username)
        feedback[username] = False

        end_msg = "AI: " + random.choice(END_MSG)
        print(end_msg)
        bot.sendMessage(chat_id, str(end_msg))

bot = telepot.Bot(BOT_TOKEN)
MessageLoop(bot, request_handler).run_as_thread()

while 1:
    time.sleep(5)
