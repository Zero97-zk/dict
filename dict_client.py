"""
dict_client.py 在线词典服务端
env: python3.6
并发:多进程
网络:tcp套接字
"""
import sys
from getpass import getpass
from socket import *


class DictClient:
    def __init__(self,host,port):
        self.host = host
        self.port = port

    # 词典客户端启动
    def start(self):
        self.connect()
        while True:
            self.print_1()
            try:
                cmd = input("请输入指令(1|2|3):")
            except KeyboardInterrupt:
                cmd = "3"
            if cmd.strip() == "1":
                self.do_register()
            elif cmd.strip() == "2":
                self.do_login()
            elif cmd.strip() == "3":
                self.do_quit()
            else:
                print("请输入正确指令")

    # 连接服务端
    def connect(self):
        self.s = socket()
        self.s.connect((self.host,self.port))

    # 一级界面
    def print_1(self):
        print("""
                 ===================
                 ++     指令      ++
                 ++   1.(注册)    ++
                 ++   2.(登录)    ++
                 ++   3.(退出)    ++
                 ===================""")

    # 注册
    def do_register(self):
        while True:
            name = input("name:")
            passwd = getpass()
            passwd1 = getpass("Again:")

            if passwd != passwd1:
                print("密码输入不一致")
                continue

            if (" " in name) or (" " in passwd):
                print("用户名和密码中不能含有空格")
                continue

            info = "R %s %s"%(name,passwd)
            self.s.send(info.encode())
            data = self.s.recv(128).decode()
            if data == "OK":
                print("注册成功")
            else:
                print(data)
                print("注册失败")
            return

    # 退出
    def do_quit(self):
        self.s.send(b"E")
        sys.exit("谢谢使用")

    # 登录
    def do_login(self):
        while True:
            name = input("name:")
            passwd = getpass()

            if (" " in name) or (" " in passwd):
                print("用户名或密码输入有误")
                return

            info = "L %s %s" % (name, passwd)
            self.s.send(info.encode())
            data = self.s.recv(128).decode()
            if data == "OK":
                print("登录成功,进入查词界面")
                self.query()
            else:
                print("登录失败")
            return

    # 查询逻辑处理
    def query(self):
        while True:
            self.print_2()
            try:
                cmd = input("请输入指令:")
            except KeyboardInterrupt:
                print("退回主界面")
                break
            if cmd.strip() == "1":
                self.word_translate()
            elif cmd.strip() == "2":
                self.record_query()
            elif cmd.strip() == "3":
                print("退回主界面")
                break

    # 二级界面
    def print_2(self):
        print("""
            ========================
            ++    1.(单词翻译)     ++
            ++    2.(查询记录)     ++
            ++    3.(注销登录)     ++
            ========================
            """)

    # 单词翻译
    def word_translate(self):
        while True:
            word = input("请输入单词(空格退出):")
            if not word:
                break
            data = "T %s"%word
            self.s.send(data.encode())
            data = self.s.recv(1024).decode()
            if data == "Fail":
                print("Sorry the word not Fount")
            else:
                print(word+":    "+data+"\n")

    # 查询历史记录
    def record_query(self):
        data = "Q "
        self.s.send(data.encode())
        data = self.s.recv(4096).decode()
        if data == "Fail":
            print("无记录")
        else:
            data_list = data.strip().split("\n")
            for i in data_list:
                data_line = i.strip().split("#")
                print(data_line[0] + ":  " + data_line[1])

# 入口
if __name__ == '__main__':
    HOST = "127.0.0.1"
    PORT = 8888
    dc = DictClient(HOST,PORT)
    dc.start()