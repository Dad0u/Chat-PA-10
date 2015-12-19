# -*- coding:utf-8 -*-

from threading import Thread
import socket
from time import *
import sys
import select
import tkinter as tk

PORT = 1148
SIZE = 2048

class Fetcher(Thread):
    def __init__(self,conn):
        Thread.__init__(self)
        self.continuer = True
        self.conn = conn
    def run(self):
        while self.continuer:
            demande = select.select([self.conn],[],[],0.2)[0]
            if len(demande) == 0:
                continue
            msg = self.conn.recv(SIZE).decode()
            print("Commande du serveur: "+msg)
            if len(msg) == 0:
                self.stop()
            if msg[:3] == "MSG":
                l = msg[4:].split("\\")
                pseudo = l[0]
                message = "\\".join(l[1:])
                fen.receive(pseudo+": "+message)
            elif msg[:3] == "ERR":
                pass
        print("Fin du fetcher")
    def stop(self):
        self.continuer = False

def command_interpreter(s):
    if s[0] != "/":
        return "MSG "+s
    if s[1:5].lower() == "nick":
        return "NIK "+s[6:]
    else:
        return None

class Fenetre():
    def __init__(self):
        self.win = tk.Tk()
        self.win.grid_rowconfigure(0, weight=1)
        self.win.grid_columnconfigure(0, weight=1)
        self.win.title('Chat PA-10')
        self.menubar = tk.Menu(self.win)
        self.filemenu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=self.filemenu)
        self.filemenu.add_command(label="Exit",command=self.win.destroy)
        self.out_text = tk.Text(self.win)
        #self.out_text.config(state=tk.DISABLED)
        self.out_text.grid(row=0, sticky=tk.W+tk.E+tk.N+tk.S)
        self.in_text = tk.Entry(self.win)
        self.in_text.grid(row=1,sticky=tk.S+tk.W+tk.E)
        self.in_text.bind('<Return>',self.send)
        self.send_button = tk.Button(command = self.send,text="Send")
        self.send_button.grid(row=1, sticky=tk.SE)
    def run(self):
        self.win.mainloop()

    def send(self, event = ''):
        s=self.in_text.get()
        self.in_text.delete(0,tk.END)
        if len(s) == 0:
            return
        s = command_interpreter(s)
        if s == None:
            self.receive('invalid command')
        else:
            connection.send(s.encode())

    def receive(self, msg):
        print(msg)
        #self.out_text.config(state=tk.ENABLED)
        self.out_text.insert(tk.END,msg+"\n")
        #self.out_text.config(state=tk.DISABLED)





address = sys.argv[-1]
connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connection.connect((address, PORT))

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
fetcher = Fetcher(connection)
fetcher.start()


fen = Fenetre()
fen.run()


fetcher.stop()
fetcher.join()
connection.close()
