# -*- coding:utf-8 -*-

from threading import Thread
import socket
#from time import sleep
import signal
import select
import sys

PORT = 1148
SIZE = 2048

class ConsoleInput(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.continuer = True
    def run(self):
        while self.continuer:
            if sys.version_info.major == 2:
                cmd = raw_input()
            else:
                cmd= input()
            if cmd == "stop":
                global continuer
                continuer = False
                self.stop()
    def stop(self):
        self.continuer = False

class Client():
    def __init__(self, conn, ip, port):
        self.logged = False
        self.ip = ip
        self.conn = conn
        self.port = port
        self.nick = ""

    def set_nick(self, nick):
        if nick in [i.nick for i in client]:
            self.conn.send("ERR Pseudo déjà pris !".encode('utf-8'))
        elif len(nick) < 3:
            self.conn.send("ERR Pseudo trop court !".encode('utf-8'))
        elif "\\" in nick:
            self.conn.send("ERR Caractère invalide dans le pseudo".encode('utf-8'))
        else:
            self.nick = nick
            self.logged = True

    def isTalking(self):
        waiting = select.select([self.conn],[],[],0)[0]
        if len(waiting) == 0:
            return False
        else:
            return True

    def disconnect(self):
        print("Deconnexion de "+self.nick)
        self.conn.close()
        client.remove(cl)

        
connection_serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connection_serv.bind(('', PORT))
connection_serv.listen(3)
continuer = True
client = []

consoleinput = ConsoleInput()
consoleinput.start()

print("Serveur lancé")
while continuer:
    new_conn = select.select([connection_serv],[],[],0.05)[0]
    for conn in new_conn:
        c,i = conn.accept()
        client.append(Client(c, *i))
        print("Nouveau client, IP: "+client[-1].ip)
    for cl in client:
        if cl.isTalking():
            print(cl.ip+" is talking!")
            try:
                msg = cl.conn.recv(SIZE).decode('utf-8')
            except:
                print("Recu un paquet bizarre ! on kicke !")
                cl.disconnect()
            print(msg)
            if len(msg) == 0:
                cl.disconnect()
                continue
            if msg[:3] == "MSG":
                message = msg[4:]
                print(cl.nick+": "+message)
                s = "MSG "+cl.nick+"\\"+message
                s = s.encode('utf-8')
                for i in client:
                    i.conn.send(s)
            elif msg[:3] == "NIK":
                cl.set_nick(msg[4:])
            elif msg == "HELLO":
                print("Commande HELLO reçue")
                cl.conn.send(b"HELLO")



print("Arrêt du serveur")
consoleinput.stop()
consoleinput.join()
for c in client:
    c.conn.close()
connection_serv.close()
