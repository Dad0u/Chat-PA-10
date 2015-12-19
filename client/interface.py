# -*- coding:utf-8 -*-

import tkinter as tk
from glob import *
from fetcher import Fetcher

def command_interpreter(s):
    if s[0] != "/":
        return "MSG "+s
    if s[1:5].lower() == "nick":
        return "NIK "+s[6:]
    elif s[1:5].lower() == "exit":
        return "EXIT"
    else:
        return None

class Fenetre():
    def __init__(self, conn):
        self.conn = conn
        self.win = tk.Tk()
        self.win.grid_rowconfigure(0, weight=1)
        self.win.grid_columnconfigure(0, weight=1)
        self.win.title('Chat PA-10')
        self.win.protocol("WM_DELETE_WINDOW", self.close) #Pour fermer proprement quand on clique sur la croix
        #self.menubar = tk.Menu(self.win)
        #self.filemenu = tk.Menu(self.menubar, tearoff=0)
        #self.menubar.add_cascade(label="File", menu=self.filemenu)
        #self.filemenu.add_command(label="Exit",command=self.close)
        self.out_text = tk.Text(self.win)
        #self.out_text.config(state=tk.DISABLED)
        self.out_text.grid(row=0, sticky=tk.W+tk.E+tk.N+tk.S)
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
        if len(s) == 0:
            return
        s = command_interpreter(s)
        if s == None:
            pass
        elif s == "EXIT":
            self.close()
        else:
            self.conn.send(s.encode('utf-8'))

    def receive(self, msg):
        print(msg)
        self.out_text.insert(tk.END,msg+"\n")

    def close(self):
        self.fetcher.stop()
        self.fetcher.join()
        self.conn.send(b'EXIT')
        self.win.destroy()
