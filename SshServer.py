import socket
import threading
import paramiko
from ServerInterface import *

import sys
from Logger import Logger
from Terminal import Terminal


class SshServer(paramiko.ServerInterface):
    def __init__(self,address,port,keyFile):

        #private attributes
        self.__isRunning = threading.Event()
        self.__socket = None 
        self.__listenThread = None 
        self.__hostKey = paramiko.RSAKey.from_private_key_file(keyFile, None)
        self.__address = address
        self.__port = port 
        self.__loop = True
        self.__channel = None
       
        
        
    def start(self):
        while(self.__loop): 
            if(not self.__isRunning.is_set()):
                try:
                    self.__isRunning.set()
                    self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.__socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    self.__socket.bind((self.__address, self.__port))
                except Exception as e:
                    print(f"failed to bind port {e}")
                    sys.exit(1)
                self.__socket.listen()
                print(f"starting the server on {self.__address}")
                print("awaiting connection...")
                conn,add = self.__socket.accept()
                print(f"client connected on {add[0]}")
                try:
                    self.__logger = Logger(add[0])
                    session = paramiko.Transport(conn)
                    session.local_version = "SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.3"
                    session.add_server_key(self.__hostKey)
                    server = ServerInterface(self.__logger)
                    session.start_server(server=server)
                    self.__channel = session.accept()
                    print("accepted connection")
                    if(session.authenticated == True):
                        print("someone has logged in")
                        self.__connectionLoop = threading.Thread(target=self.__connectionLoop, args=(self.__channel,))
                        self.__connectionLoop.start()
                    else:
                        self.__logger.updateStatus("login fail")
                        self.__logger.writeLogFile()
                        print("restarting...")
                except paramiko.SSHException:
                    print(f"error in sending banner to client: {add[0]}")
                    self.__logger.updateStatus("bannerError")
                    self.__logger.writeLogFile()
                    print("restarting...")
                except:                
                    print(f"{add[0]} has probed the server")
                    self.__logger.updateStatus("probed")
                    self.__logger.writeLogFile()
                    print("restarting...")
                
            else:
                print("clearing thread")
                self.__isRunning = threading.Event()

  





    def __connectionLoop(self,channel):
        if(channel == None):
            print("no channel vlaue")
            print(self.__channel)
            channel = self.__channel
        seed = self.__logger.clientIP + self.__logger.time
        terminal = Terminal()
        self.__logger.updateStatus("login")
        terminal.setLogger(self.__logger)
        #channel.send(terminal.getFilePointer())
        loop = True
        #print banner
        #channel.send("\n")
        bannerList = terminal.outputTxt("banner.txt")#this is bad but idc, about tech debt
        for i in bannerList:
            channel.send(i)
        channel.send("\n\r")
        channel.send(terminal.getFilePointer())
        while loop:
            clientMessage = channel.recv(1024)
            messageList = terminal.handleInput(clientMessage)
            if(messageList is not None):
                for i in messageList:
                    
                    if(i != "quit"):
                        if(type(i)==list):
                            for x in i:
                                channel.send(x)
                        else:
                            try:
                                channel.send(i)
                            except:
                                print("connection closed")
                                loop = False
                                break
                    else:
                        #channel.send(b"\x1b[2J\x1b[H")
                        loop = False
                        self.__loop = False
                        print("client has quit out the honeypot \r\n shutting down! ")
                       
        self.__logger.writeLogFile()
            







  