# -*- coding:utf-8 -*-

import sys
if sys.version_info.major == 2:
    print("Ce programme est prévu pour fonctionner avec Python3 !")
    sys.exit(-1)
import socket
from client import Client
from consoleInput import ConsoleInput
from process_cmd import process_cmd
from glob import *
import select

def prepare(s):
    if len(s) > 2**16-3:
        print('Message trop long !')
    s = s[:2**16-3]
    s = s.encode('utf-8')
    s = bytes([len(s)//256,len(s)%256])+s
    return(s)

def hello(client):
    if client.connected:
        client.conn.send(prepare('NFO You are already connected'))
    else:
        client.conn.send(prepare('HELLO'))
        client.connected = True

def send_to_all(msg, sender=None):
    if sender == None:
        s = prepare(msg)
        for cl in client:
            cl.conn.send(s)
        return
    if not sender.logged:
        if OPEN:
            sender.conn.send(prepare("ERR You must choose a nickname first, use /nick <nickname> to do so"))
        else:
            sender.conn.send(prepare("ERR You are not logged in."))
        return
    s = prepare("MSG "+sender.nick+"\\"+msg)
    for cl in client:
        cl.conn.send(s)

def change_nick(cl, nick):
    if nick in [i.nick for i in client]:
        cl.conn.send(prepare('ERR Nickname already in use'))
        return
    elif len(nick) < 3:
        cl.conn.send(prepare('ERR Nickname too short (at least 3 characters)'))
        return
    elif "\\" in nick:
        cl.conn.send(prepare('ERR Invalid character in nickname'))
        return
    else:
        old_nick = cl.nick
        cl.set_nick(nick)
        if cl.logged:
            s = "NFO "+old_nick+" is now known as "+nick
            print('Nouveau pseudo de {}: {}'.format(old_nick,nick))
            send_to_all(s)
        else:
            print('Le client {} a choisi le pseudo {}'.format(cl.ip,nick))
            cl.conn.send(prepare("NFO Succesfully changed your nickname to "+nick))
        if OPEN and cl.logged == False:
            cl.logged = True
            cl.conn.send(prepare('NFO You are now logged in'))
            send_to_all('NFO '+cl.nick+' joined the chat.')

def private(msg, client, sender = None):
    if sender == None:
        client.conn.send(prepare("NFO "+msg))
    else:
        s = "MSG "+sender.nick+" (private)\\"+msg
        client.conn.send(prepare(s))
        s = "MSG [Private message to "+client.nick+"]\\"+msg
        sender.conn.send(prepare(s))

def find_client(nick):
    words = nick.split(' ')
    ret = []
    for i in range(len(words)):
        s = " ".join(words[:i+1])
        for cl in client:
            if cl.nick == s:
                ret.append(cl)
    if len(ret) == 0:
        return None
    elif len(ret) == 1:
        return ret[0]
    else:
        longest = ret[0]
        for i in ret:
            if len(i.nick) > len(longest.nick):
                longest = i
        return longest

def help(cl):
    s = """List of available commands: 
/nick <nick> - To set your nickname
/help - To see this message
/msg <user> <msg> - To send a private message to user
/list - To get the list of current users
/exit - To disconnect and leave"""
    cl.conn.send(prepare('NFO '+s))

def send_list(target):
    s = ''
    n = 0
    for cl in client:
        if cl.logged:
            n+=1
            s = s+cl.nick+"\n"
    s = str(n)+" client(s) connected:\n"+s[:-1]
    target.conn.send(prepare('NFO '+s))

connection_serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connection_serv.bind(('', PORT))
connection_serv.listen(3)
continuer = True
client = []

consoleinput = ConsoleInput()
consoleinput.start()

print("Serveur lancé")
while consoleinput.continuer:

    if len(consoleinput.queue) != 0:        #Interprète les commandes console du serveur
        for s in consoleinput.queue:
            if s[0] == "kick":
                cl = find_client(s[1])
                if cl != None:
                    send_to_all("NFO "+cl.nick+" was kicked by the server.")
                    cl.disconnect()
                    client.remove(cl)
                else:
                    print("Client not found: "+s[1])
            elif s[0] == "list":
                print("User list:")
                for i in client:                    
                    print(i.nick)
            consoleinput.queue.remove(s)


    new_conn = select.select([connection_serv],[],[],0.05)[0]   #Ajout des nouveaux clients
    for conn in new_conn:
        c,i = conn.accept()
        client.append(Client(c, *i))
        print("Nouveau client, IP: "+client[-1].ip)

    for cl in client:                               #Traitement des messages reçus.
        if cl.isTalking():
            #print(cl.ip+" is talking!")
            try:
                msg = cl.conn.recv(SIZE)
            except:
                print("Recu un paquet bizarre, on kicke !")
                cl.disconnect()
                client.remove(cl)
            if len(msg) == 0:
                cl.disconnect()
            queue = []
            while msg != b'':
                #print(msg)
                longueur = 256*msg[0]+msg[1]
                #if longueur > 1024:
                #    print('/!\\ Oddly long message incoming ({} bytes).'.format(longueur))
                #    print(msg)
                while len(msg) < longueur+2:
                    #print('Attente du paquet suivant, reçu {}/{} octets'.format(len(msg),longueur+2))
                    demande = select.select([cl.conn],[],[],3)[0]
                    if len(demande) == 0:
                        #print('Non reçu !')
                        print('Warning: Message incomplet reçu !')
                        longueur = len(msg) - 2
                    else:
                        msg = msg + cl.conn.recv(SIZE)
                    #print('reçu !')
                queue.append(msg[2:longueur+2].decode('utf-8'))
                msg = msg[longueur+2:]
            for msg in queue:
                action, s = process_cmd(msg)
                if action == DISC:
                    if cl.logged:
                        send_to_all("NFO "+cl.nick+" left the chat.")
                    cl.disconnect()
                    client.remove(cl)
                elif action == TOALL:
                    print(cl.nick+" ("+cl.ip+"): "+s)
                    send_to_all(s,cl)
                elif action == HELLO:
                    hello(cl)
                elif action == CHGNICK:
                    change_nick(cl,s)
                elif action == TOCLIENT:
                    target = find_client(s)
                    if target == None:
                        cl.conn.send(prepare("NFO User not found"))
                    elif cl.connected == True:
                        print("Private message from "+cl.nick+" to "+target.nick+": "+s[len(cl.nick)+5:])
                        private(s[len(target.nick)+1:],target,cl)
                    else:
                        if OPEN:
                            sender.conn.send(prepare("ERR You must choose a nickname first, use /nick <nickname> to do so"))
                        else:
                            sender.conn.send(prepare("ERR You are not logged in."))
                elif action == HELP:
                    help(cl)
                elif action == LIST:
                    send_list(cl)

print("Arrêt du serveur")
consoleinput.join()
for c in client:
    c.disconnect()
connection_serv.close()
