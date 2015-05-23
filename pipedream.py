#!/usr/bin/python

import os
import sys
import getopt
import socket
import thread
import random
import pickle

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# The sun is a wondrous body, like a magnificent father - if only I could be
#                      so ~grossly incandescent~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

VERSION="v0p1"

class socketMessage:
  def __init__(self,direction,):
    self.

def replay(_outHost,file):
  (outHost,outPort) = _outHost.split(":")
  print "[replay: %s:%d - %s]" % (outHost,int(outPort),file)

# only start this when there's a connection
def captureserver(clientsock,addr,_outHost,file,tag):
  BUFSIZE = 10240
  (outHost,outPort) = _outHost.split(":")
  forwardSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
  forwardSocket.connect( (outHost,int(outPort)) )
  # okay, set timeouts.
  forwardSocket.settimeout(1)
  clientsock.settimeout(1)
  while True:
    try:
      data = clientsock.recv(BUFSIZE)
      if not data: break
      forwardSocket.sendall(data)
    except socket.timeout, e:
      pass
      # print "timeerror - forward"
    except:
      # print "dying"
      break
    try:
      data = forwardSocket.recv(BUFSIZE)
      if not data: break
      clientsock.sendall(data)
    except socket.timeout, e:
      pass
      # print "timeerror - back"
    except:
      # print "dying"
      break
  print "[close: %04x]" % tag
  forwardSocket.close()
  clientsock.close()

def capture(_inHost,_outHost,file):
  (inHost,inPort) = _inHost.split(":")
  (outHost,outPort) = _outHost.split(":")
  serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  serversocket.bind( (inHost,int(inPort)) )
  serversocket.listen(5)
  print "[%s:%d -> PROXY -> %s:%d] -> [%s]" % (inHost,int(inPort),outHost,int(outPort),file)
  while True:
    (clientsocket,address) = serversocket.accept()
    tag = random.randint(0,0xFFFF)
    print "[open: %04x]" % tag
    thread.start_new_thread(captureserver, (clientsocket,address,_outHost,file,tag))

def usage():
  print "-----------------------------------------"
  print " project pipedream"
  print "-----------------------------------------"
  print " -i port : listening socket"
  print " -o host:port : output socket"
  print " -m [capture|replay] : select mode"
  print " -f filename : load or save to file"
  print " -h : help"
  print "-----------------------------------------"

def main():
  inHost = None
  outHost = None
  mode = None
  file = None
  try:
    optlist,args = getopt.getopt(sys.argv[1:],"i:o:m:f:h",["in","out","mode","file","help"])
  except getopt.GetoptError as err:
    print str(err)
    usage()
    sys.exit(2)
  for (o,a) in optlist:
    if o in ("-i","--in"):
      inHost = a
    elif o in ("-o","--out"):
      outHost = a
    elif o in ("-m","--mode"):
      mode = a
    elif o in ("-f","--file"):
      file = a
    elif o in ("-m","--mode"):
      mode = a
    elif o in ("-h","--help"):
      usage()
      sys.exit(2)
    else:
      print "error: unknown argument %s" % o
  if mode == "capture" and inHost is not None and outHost is not None and file is not None:
    capture(inHost,outHost,file)
  elif mode == "replay" and outHost is not None and file is not None:
    replay(outHost,file)
  else:
    print "nope"
    sys.exit(0)

if __name__ == "__main__":
  main()
