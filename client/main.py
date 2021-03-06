# -*- coding:utf-8 -*-
"""
Programme par Victor Couty (victor@couty.eu)
Client du programme de chat PA-10
Utilisation: python3 main.py ip[:port]
Taper /help une fois le client connecté pour avoir la liste des commandes.
NB: nécessite tkinter (apt-get install python3-tk)
"""
import sys
if sys.version_info.major == 2:
    print("Ce programme est prévu pour fonctionner avec Python3 !")
    sys.exit(-1)
import socket
import select
from interface import Fenetre
from glob import *

def auth(connection):
    connection.send(bytes([0,6])+b"/HELLO")
    replying = select.select([connection],[],[],5)[0]
    if len(replying) == 0:
        print("Aucune réponse du serveur !")
        sys.exit(0)
    else:
        reply = replying[0].recv(SIZE)
    if reply != bytes([0,5])+b"HELLO":
        print("Réponse invalide du serveur: "+reply.decode())
        sys.exit(0)
    print("Connection réussie")

port = DEFAULT_PORT
#address = sys.argv[-1]

address = input("Adresse du serveur ? ")

if ':' in address:
    address,port = address.split(":")
    port = int(port)
    
connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connection.connect((address, port))
auth(connection)
fen = Fenetre(connection)
fen.run()

connection.close()
