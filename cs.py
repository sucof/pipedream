#!/usr/bin/python

import socket
import random
import thread
import ssl
from sm import *

def captureserver(clientsock,addr,_outHost,file,tag,sslreq):
  BUFSIZE = 10240
  conv = socketConversation()
  (outHost,outPort) = _outHost.split(":")
  if sslreq:
    forwardSocket_ = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    forwardSocket = ssl.wrap_socket(forwardSocket_,cert_reqs=ssl.CERT_NONE)
  else:
    forwardSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
  forwardSocket.connect( (outHost,int(outPort)) )
  forwardSocket.settimeout(2)
  clientsock.settimeout(2)
  while True:
    try:
      data = clientsock.recv(BUFSIZE)
      if not data: break
      forwardSocket.sendall(data)
      conv.appendMessage(socketConversation.DIRECTION_FORWARD,data)
    except socket.timeout:
      pass
    except ssl.SSLError, e: 
      if e.errno is None:
        pass
      else:
        print "[err: %s]" % e.message
        break
    try:
      data = forwardSocket.recv(BUFSIZE)
      if not data: break
      clientsock.sendall(data)
      conv.appendMessage(socketConversation.DIRECTION_BACK,data)
    except socket.timeout:
      pass
    except ssl.SSLError, e:
      if e.errno is None:
        pass
      else:
        print "[err: %s]" % e.message
        break
  print "[close: %04x]" % tag
  conv.saveToFile("%s-%d.cnv" % (file,tag))
  forwardSocket.close()
  clientsock.close()

def capture(_inHost,_outHost,file,sslreq):
  (inHost,inPort) = _inHost.split(":")
  (outHost,outPort) = _outHost.split(":")
  serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  serversocket.bind( (inHost,int(inPort)) )
  serversocket.listen(5)
  print "[%s:%d -> PROXY -> %s:%d] -> [%s]" % (inHost,int(inPort),outHost,int(outPort),file)
  while True:
    if sslreq:
      (clientsocket_,address) = serversocket.accept()
      clientsocket = ssl.wrap_socket(clientsocket_,server_side = True,certfile="server.crt",keyfile="server.key")
    else:
      (clientsocket,address) = serversocket.accept()
    tag = random.randint(0,0xFFFF)
    print "[open: %04x]" % tag
    thread.start_new_thread(captureserver, (clientsocket,address,_outHost,file,tag,sslreq))