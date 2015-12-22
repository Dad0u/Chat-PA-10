# -*- coding:utf-8 -*-

from glob import *

def process_cmd(msg):
    if len(msg) == 0:
        return DISC,None
    elif msg == "/exit":
        return DISC,None
    elif msg[:6] == "/nick ":
        return CHGNICK,msg[6:]
    elif msg == "/HELLO":
        return HELLO,None
    elif msg[:5] == "/msg ":
        l = msg[5:].split(" ")
        pseudo = l[0]
        message = " ".join(l[1:])
        return TOCLIENT,(pseudo,message)
    elif msg == "/help":
        return HELP,None
    elif msg == "/list":
        return LIST, None
    else:
        return TOALL,msg
