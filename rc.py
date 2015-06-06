#!/usr/bin/python
#!/usr/bin/python

import socket
import random
import thread
import ssl
from sm import *

class replayClient:
  def __init__(self,outHost,outPort,socketConv,sslreq,mutChance):
    self.outHost = outHost
    self.outPort = outPort
    self.socketConv = socketConv
    self.sslreq = sslreq
    self.mutChance = mutChance

  def connect(self):
    if self.sslreq:
      forwardSocket_ = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
      forwardSocket = ssl.wrap_socket(forwardSocket_,cert_reqs=ssl.CERT_NONE)
    else:
      forwardSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    forwardSocket.connect( (self.outHost, int(self.outPort)) )
    forwardSocket.settimeout(1)
    self.forwardSocket = forwardSocket

  def play(self):
    forwardSocket = self.forwardSocket
    for i in range(0,len(self.socketConv.messages)):
      (d,m) = self.socketConv.fetchMessage(i)
      if d == socketConversation.DIRECTION_FORWARD:
        a = random.randint(0,100)
        if a <= self.mutChance:
          forwardSocket.sendall(self.socketConv.fetchMutated(i))
        else:
          forwardSocket.sendall(m)
      else:
        if self.socketConv.messages[i].mandatory == True:
          forwardSocket.settimeout(10000)
        else:
          forwardSocket.settimeout(1)
        try:
          data = forwardSocket.recv(10240)
          if not data:
            continue
          for m in self.socketConv.messages:
            if m.direction == socketMessage.DIRECTION_FORWARD:
              if m.checkBind(data):
                forwardSocket.sendall(m.message)
                break
        except socket.timeout:
          pass
        except ssl.SSLError, e:
          if e.errno is None:
            pass
          else:
            print "[err: %s]" % e.message
            break

  def disconnect(self):
    self.forwardSocket.close()

def replayclient(_outHost,file,sslreq,mutChance):
  (outHost,outPort) = _outHost.split(":")
  print "[replay client: %s:%d - %s]" % (outHost,int(outPort),file)
  conv = socketConversation(file)
  rc = replayClient(outHost, outPort, conv, sslreq, mutChance)
  print "[success]"
  rc.connect()
  rc.play()
  rc.disconnect()
