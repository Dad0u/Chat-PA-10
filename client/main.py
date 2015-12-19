#coding: utf-8

from threading import Thread
import socket
from time import *
import sys
import select

PORT = 1148
SIZE = 2048

class Getter(Thread):
    def __init__(self,conn):
        Thread.__init__(self)
        self.continuer = True
        self.conn = conn
    def run(self):
        while self.continuer:
            demande = select.select([self.conn],[],[],0.2)
            print("lulu")
            if len(demande) == 0:
                continue
            msg = self.conn.recv(SIZE).decode()
            print("Commande du serveur: "+msg)
            if len(msg) == 0:
                print("reçu du vide, sortie du getter")
                self.stop()
            if msg[:3] == "MSG":
                l = msg[3:].split("\\")
                pseudo = l[0]
                message = "\\".join(l[1:])
                print(pseudo+": "+message)
            elif msg[:3] == "ERR":
                pass
        print("sortie du getter")
    def stop(self):
        self.continuer = False



address = sys.argv[-1]
connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connection.connect((address, PORT))

connection.send(b"HELLO")
replying = select.select([connection],[],[],5)[0]
if len(replying) == 0:
    print("Aucune réponse du serveur !")
    sys.exit(0)
else:
    print("a")
    reply = replying[0].recv(SIZE)
    print("b")
if reply != b"HELLO":
    print("Réponse invalide du serveur: "+reply.decode())
    sys.exit(0)
print("Connection réussie")
print("Choisir le pseudo:")
if sys.version_info.major == 2:
    msg = raw_input("> ")
else:
    msg = input("> ")
s = "NIK "+msg
s = s.encode()
connection.send(s)
getter = Getter(connection)
getter.start()
msg = ""
while True:
    if sys.version_info.major == 2:
        msg = raw_input("> ")
    else:
        msg = input("> ")
    if msg == "exit":
        break
    connection.send(b"MSG "+msg.encode())
getter.stop()
getter.join()
connection.close()
