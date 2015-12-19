# -*- coding:utf-8 -*-

#from threading import Thread
import socket
from client import Client
from consoleInput import ConsoleInput
from process_cmd import process_cmd
from glob import *

import select
import sys


def send_to_all(msg, sender):
    if not sender.logged:
        if OPEN:
            sender.conn.send("ERR You must choose a nickname first, use /nick <nickname> to do so".encode('utf-8'))
        else:
            sender.conn.send("ERR You are not logged in.".encode('utf-8'))
        return
    s = "MSG "+sender.nick+"\\"+msg
    s = s.encode('utf-8')
    for cl in client:
        cl.conn.send(s)

def change_nick(cl, nick):
    if nick in [i.nick for i in client]:
        cl.conn.send('ERR Nickname already in use'.encode('utf-8'))
        return
    elif len(nick) < 3:
        cl.conn.send('ERR Nickname too short (at least 3 characters)'.encode('utf-8'))
        return
    elif "\\" in nick:
        cl.conn.send('ERR Invalid character in nickname')
        return
    else:
        cl.set_nick(nick)
        cl.conn.send(b"MSG Succesfully changed your nickname to "+nick.encode())
        if OPEN:
            cl.logged = True


        
connection_serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connection_serv.bind(('', PORT))
connection_serv.listen(3)
continuer = True
client = []

consoleinput = ConsoleInput()
consoleinput.start()

print("Serveur lancé")
while consoleinput.continuer:
    new_conn = select.select([connection_serv],[],[],0.05)[0]
    for conn in new_conn:
        c,i = conn.accept()
        client.append(Client(c, *i))
        print("Nouveau client, IP: "+client[-1].ip)

    for cl in client:
        if cl.isTalking():
            #print(cl.ip+" is talking!")
            try:
                msg = cl.conn.recv(SIZE).decode('utf-8')
            except:
                print("Recu un paquet bizarre, on kicke !")
                cl.disconnect()
                client.remove(cl)
            #print(msg)

            action, s = process_cmd(msg)
            if action == DISC:
                cl.disconnect()
                client.remove(cl)
            elif action == TOALL:
                send_to_all(s,cl)
            elif action == TOSELF:
                cl.conn.send(s)
            elif action == CHGNICK:
                change_nick(cl,s)


print("Arrêt du serveur")
consoleinput.join()
for c in client:
    c.conn.close()
connection_serv.close()
