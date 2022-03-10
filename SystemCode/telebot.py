import telebot
# from telebot import TeleBot
from config import *
import time
import os
import random

# https://github.com/eternnoir/pyTelegramBotAPI
bot = telebot.TeleBot(telegram_botTOKEN)
# bot.poll(debug=True)
bot.infinity_polling()


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Howdy, how are you doing?")


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, message.text)
    print(message, message.text)


'''
@bot.message_handler(commands=['start'])
def start_command(message):
    rdm = random.randint(0, 1)
    bot.send_message(message.chat.id, welcome_msg[rdm])

@bot.route('/chat')
def chat_command(message):
   keyboard = telebot.types.InlineKeyboardMarkup()
   keyboard.add(
       telebot.types.InlineKeyboardButton(
           'Message the developer', url='telegram.me/artiomtb'
       )
   )
   bot.send_message(
       message.chat.id, "Tell me about your feelings", reply_markup=keyboard
   )

@bot.route('/command ?(.*)')
def example_command(message, cmd):
    chat_id_dest = message['chat']['id']
    msg = "Command Received: {}".format(cmd)
    print("SD", chat_id_dest, msg)
    bot.send_message(chat_id_dest, msg)

@bot.route('(?!/).+')
def parrot(message):
   chat_id_dest = message['chat']['id']
   user_msg = message['text']
   print(chat_id_dest, user_msg)
   msg = "Parrot Says: {}".format(user_msg)
   bot.send_message(chat_id_dest, msg)

@bot.route('/chat')
def parrot(message):
   chat_id_dest = message['chat']['id']
   user_msg = message['text']
   print(chat_id_dest, user_msg)
   msg = "How are you feeling: {}".format(user_msg)
   bot.send_message(chat_id_dest, msg)
'''


