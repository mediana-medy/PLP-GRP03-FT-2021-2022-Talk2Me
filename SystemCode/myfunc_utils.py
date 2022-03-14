from config import *

def chat_func(msg):

    exec(open('conversation/conv_interact.py').read())


def hotline_func(msg):
    return ""