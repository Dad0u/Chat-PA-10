# -*- coding:utf-8 -*-

from glob import *

def process_cmd(msg):
    if len(msg) == 0:
        return DISC,None
    elif msg == "EXIT":
        return DISC,None

    elif msg[:4] == "MSG ":
        message = msg[4:]
        return TOALL,message

    elif msg[:4] == "NIK ":
        return CHGNICK,msg[4:]

    elif msg == "HELLO":
        return TOSELF,b"HELLO"

    elif msg[:4] == "PRV":
        l = msg[4:].split("\\")
        pseudo = l[0]
        message = "\\".join(l[1:])
        return TOCLIENT,(pseudo,message)
