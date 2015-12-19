# -*- coding:utf-8 -*-


import socket
from time import *
import sys
import select
from interface import Fenetre
#from fetcher import Fetcher
from glob import *

PORT = 1148
SIZE = 2048


def auth(connection):
    connection.send(b"HELLO")
    replying = select.select([connection],[],[],5)[0]
    if len(replying) == 0:
        print("Aucune réponse du serveur !")
        sys.exit(0)
    else:
        reply = replying[0].recv(SIZE)
    if reply != b"HELLO":
        print("Réponse invalide du serveur: "+reply.decode())
        sys.exit(0)
    print("Connection réussie")



address = sys.argv[-1]
connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connection.connect((address, PORT))

auth(connection)




fen = Fenetre(connection)
fen.run()


connection.close()
