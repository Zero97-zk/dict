"""
dict_server.py 在线词典服务端
env: python3.6
并发:多进程
网络:tcp套接字
"""

from socket import *
from multiprocessing import Process
import signal
import os,sys
from dict_db import *

# 处理僵尸进程
signal.signal(signal.SIGCHLD,signal.SIG_IGN)


class DictServer:
    def __init__(self,host,port):
        self.host = host
        self.port = port
        self.db = Database()
        self.socket_() # 网络搭建
        self.username = None

    # 客户端处理函数
    def handle(self,c):
        while True:
            data = c.recv(1024).decode()
            tmp = data.split(" ")
            if not tmp or tmp[0] == "E":
                sys.exit()
            elif tmp[0] == "R":
                self.register(c,tmp[1],tmp[2])
            elif tmp[0] == "L":
                self.login(c,tmp[1],tmp[2])
            elif tmp[0] =="T":
                self.translate(c,tmp[1])
            elif tmp[0] == "Q":
                self.record_query(c)

    # 词典服务端启动函数
    def start(self):
        while True:
            try:
                c, addr = self.s.accept()
                print("Connect from",addr)
            except KeyboardInterrupt:
                self.db.close()
                os._exit(0)
            except Exception as e:
                print(e)
                continue
            p = Process(target=self.handle,args=(c,))
            p.start()

    # 网络搭建
    def socket_(self):
        self.s = socket()
        self.s.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
        self.s.bind((self.host,self.port))
        self.s.listen(5)
        print("Listen the port 8888 ...")

    # 注册处理
    def register(self, c, name, passwd):
        if self.db.register(name,passwd):
            c.send(b"OK")
        else:
            c.send("Sorry your username already exist".encode())

    # 登录处理
    def login(self, c, name, passwd):
        if self.db.login(name,passwd):
            c.send(b"OK")
            self.username = name
        else:
            c.send(b"Fail")

    # 单词翻译处理
    def translate(self,c, word):
        mean = self.db.translate(word,self.username)
        if mean:
            c.send(mean.encode())
        else:
            c.send(b"Fail")

    # 记录查询处理
    def record_query(self, c):
        record_tuple = self.db.record_query(self.username)
        if record_tuple:
            record =""
            for i in record_tuple:
                for j in i:
                    record += str(j)+"#"
                record += "\n"
            c.send(record.encode())
        else:
            c.send(b"Fail")

# 入口
if __name__ == '__main__':
    HOST = "0.0.0.0"
    PORT = 8888
    ds = DictServer(HOST,PORT)
    ds.start()



