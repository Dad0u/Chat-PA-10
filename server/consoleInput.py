# -*- coding:utf-8 -*-

from  threading import Thread
import sys

class ConsoleInput(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.continuer = True

    def run(self):
        while self.continuer:
            cmd = input()
            if cmd == "stop":
                self.stop()

    def stop(self):
        self.continuer = False
