# -*- coding:utf-8 -*-

import select
from threading import Thread
from glob import *

class Fetcher(Thread):
    def __init__(self,conn, write):
        Thread.__init__(self)
        self.continuer = True
        self.conn = conn
        self.write = write
        self.queue = []

    def run(self):
        while self.continuer:
            demande = select.select([self.conn],[],[],0.2)[0]
            if len(demande) == 0:
                continue
            msg = self.conn.recv(SIZE)
            queue = []
            #print(msg)
            while msg != b'':
                longueur = 256*msg[0]+msg[1]
                #if longueur > 1024:
                #    print('/!\\ Oddly long message incoming ({} bytes).'.format(longueur))
                #    print(msg)
                while len(msg) < longueur+2:
                    #print('Attente du paquet suivant, reçu {}/{} octets'.format(len(msg),longueur+2))
                    demande = select.select([self.conn],[],[],3)[0]
                    if len(demande) == 0:
                        #print('Non reçu !')
                        self.write('Warning','Message incomplet reçu !',RED)
                        longueur = len(msg) - 2
                    else:
                        msg = msg + self.conn.recv(SIZE)
                    #print('reçu !')
                queue.append(msg[2:longueur+2].decode('utf-8'))
                msg = msg[longueur+2:]
            #print("Commandes du serveur: "+str(queue))
            for msg in queue:
                if len(msg) == 0:
                    self.stop()
                if msg[:3] == "MSG":
                    l = msg[4:].split("\\")
                    pseudo = l[0]
                    message = "\\".join(l[1:])
                    self.write(pseudo,message,GREEN)
                elif msg[:3] == "ERR":
                    self.write("Erreur",msg[4:],RED)
                elif msg[:3] == "NFO":
                    self.write("Info",msg[4:],ORANGE)
                elif msg[:3] == "EXT":
                    self.write("Info","Déconnecté par le serveur !",ORANGE)
                    self.conn.close()
                    self.stop()
                else:
                    self.write("Erreur","Message inconnu du serveur: "+msg,RED)
        print("Fin du fetcher")

    def stop(self):
        self.continuer = False
