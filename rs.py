#!/usr/bin/python

import socket
import random
import thread
import ssl
from sm import *

def replayserver(_inHost,file,sslreq,mutChance):
  (inHost,inPort) = _inHost.split(":")
  # rs = replayServer(inHost,inPort,socketConversation(file),sslreq,mutChance)
  # print "[replay server: %s:%d - %s]" % (inHost, int(inPort),file)
  conv = socketConversation(file)
  rs = replayServer(inHost,inPort,conv,sslreq,mutChance)
  print "[replay server: %s:%d - %s]" % (inHost, int(inPort),file)
  rs.run()

class replayServer:
  def __init__(self,inHost,inPort,socketConv,sslreq,mutChance):
    self.inHost = inHost
    self.inPort = inPort
    self.socketConv = socketConv
    self.sslreq = sslreq
    self.mutChance = mutChance

  def run(self):
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.bind( (self.inHost,int(self.inPort)) )
    serversocket.listen(5)
    while True:
      if self.sslreq:
        (clientsocket_,address) = serversocket.accept()
        clientsocket = ssl.wrap_socket(clientsocket_,server_side = True,certfile="server.crt",keyfile="server.key")
      else:
        (clientsocket,address) = serversocket.accept()
      thread.start_new_thread(self.replay_handler,(clientsocket,address))

  def replay_handler(self,clientsock,address):
    # if the first message is a server message...
    if self.socketConv.messages[0].mandatory is True and self.socketconv.messages[i].direction == socketMessage.DIRECTION_BACK:
      if random.randint(0,100) <= self.mutChance:
        clientsock.sendall(self.socketConv.fetchMutated(0))
      else:
        clientsock.sendall(self.socketConv.messages[0].message)
    clientsock.settimeout(3)
    while True:
      try:
        data = clientsock.recv(10240)
        if not data: break
      except socket.error, e:
        if e.errno == 10054:
          print "[client disconnected]"
          return
      except socket.timeout:
        pass
      except ssl.SSLError, e:
        if e.errno is None:
          pass
        else:
          print "[err: %s]" % e.message
          break
      try:
        for m in range(0,len(self.socketConv.messages)):
          if self.socketConv.messages[m].checkBind(data):
            if random.randint(0,100) <= self.mutChance:
              clientsock.sendall(self.socketConv.fetchMutated(m))
            else:
              clientsock.sendall(self.socketConv.messages[m].message)
            break
      except:
        continue
