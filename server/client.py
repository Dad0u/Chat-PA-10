# -*- coding:utf-8 -*-

import select

class Client():
    def __init__(self, conn, ip, port):
        self.logged = False
        self.connected = False
        self.ip = ip
        self.conn = conn
        self.port = port
        self.nick = ""

    def set_nick(self, nick):
        self.nick = nick

    def isTalking(self):
        waiting = select.select([self.conn],[],[],0)[0]
        if len(waiting) == 0:
            return False
        else:
            return True

    def disconnect(self):
        if self.logged:
            print("Deconnexion de "+self.nick)
        else:
            print("Deconnexion du client non authentifié "+self.ip)
        try:
            self.conn.send(bytes([0,3])+b'EXT')
        except:
            pass
        self.conn.close()
