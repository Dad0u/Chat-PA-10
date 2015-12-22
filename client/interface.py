# -*- coding:utf-8 -*-

import tkinter as tk
from glob import *
from fetcher import Fetcher

class Fenetre():
    def __init__(self, conn):
        self.conn = conn
        self.win = tk.Tk()
        self.win.grid_rowconfigure(0, weight=1)
        self.win.grid_columnconfigure(0, weight=1)
        self.win.title('Chat PA-10')
        self.win.protocol("WM_DELETE_WINDOW", self.close) #Pour fermer proprement quand on clique sur la croix
        self.out_text = tk.Text(self.win)
        self.out_text.grid(row=0, sticky=tk.W+tk.E+tk.N+tk.S)
        self.out_text.configure(state='disabled')
        self.in_text = tk.Entry(self.win)
        self.in_text.grid(row=1,sticky=tk.S+tk.W+tk.E)
        self.in_text.bind('<Return>',self.send)
        self.send_button = tk.Button(command = self.send,text="Send")
        self.send_button.grid(row=1, sticky=tk.SE)
        self.fetcher = Fetcher(conn, self.receive)

    def run(self):
        self.fetcher.start()
        self.win.mainloop()

    def send(self, event = ''):
        s=self.in_text.get()
        self.in_text.delete(0,tk.END)
        if len(s) == 0 or len(s.encode('utf-8')) > 2**16 - 3:
            return
        elif s == "/exit":
            self.close()
        else:
            s = s.encode('utf-8')
            #print(s)
            self.conn.send(bytes([len(s)//256,len(s)%256])+s)

    def receive(self, msg):
        print(msg)
        self.out_text.configure(state='normal')
        self.out_text.insert(tk.END,msg+"\n")
        self.out_text.configure(state='disabled')

    def close(self):
        self.fetcher.stop()
        self.fetcher.join()
        self.conn.send(bytes([0,5])+b'/exit')
        self.win.destroy()
