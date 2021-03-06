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
        self.out_text = tk.Text(self.win,wrap=tk.WORD)
        self.out_text.grid(row=0,column=0,columnspan=2,sticky=tk.W+tk.E+tk.N+tk.S)
        self.out_text.configure(state='disabled')
        self.scrollbar = tk.Scrollbar(self.win)
        self.scrollbar.grid(row=0,column=2, sticky = tk.E+tk.N+tk.S)
        self.out_text.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.out_text.yview)
        self.in_text = tk.Entry(self.win)
        self.in_text.grid(row=1,column=0,sticky=tk.W+tk.E)
        self.in_text.bind('<Return>',self.send)
        self.send_button = tk.Button(command = self.send,text="Send")
        self.send_button.grid(row=1,column=1,columnspan=2, sticky=tk.SE)
        self.fetcher = Fetcher(conn, self.receive)
        for color in [RED,ORANGE,GREEN]:
          self.out_text.tag_config(color,foreground=color)

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

    def receive(self, header, msg, color):
        print(msg)
        self.out_text.configure(state='normal')
        self.out_text.insert(tk.END,header+": ",color)
        self.out_text.insert(tk.END,msg+"\n")
        self.out_text.configure(state='disabled')
        self.out_text.see(tk.END)

    def close(self):
        self.fetcher.stop()
        self.fetcher.join()
        try:
            self.conn.send(bytes([0,5])+b'/exit')
        except:
            pass
        self.win.destroy()
