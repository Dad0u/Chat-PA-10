# -*- coding:utf-8 -*-

from  threading import Thread
import sys

class ConsoleInput(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.continuer = True
        self.queue = []

    def run(self):
        while self.continuer:
            cmd = input()
            if cmd == "stop":
                self.stop()
            elif cmd[:5] == "kick ":
                self.queue.append(("kick",cmd[5:]))
            elif cmd == "list":
                self.queue.append(("list",None))
            elif cmd == "help":
                print('Commands: stop, kick <user>, list, help, say')
            elif cmd[:4] == "say ":
                self.queue.append(("say",cmd[4:]))
            else:
                print("Command not found, type help to have a list of available commands")

    def stop(self):
        self.continuer = False
