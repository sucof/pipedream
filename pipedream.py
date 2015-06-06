#!/usr/bin/python

import os
import sys
import ssl
import getopt
import socket
import thread
import random
import pickle
import string
from sm import *
from rs import *
from rc import *
from cs import *
from ce import *

def usage():
  print "-----------------------------------------"
  print " project pipedream"
  print "-----------------------------------------"
  print " -i host:port : listening socket"
  print " -o host:port : output socket"
  print " -m [capture|replay|edit] : select mode"
  print " -f filename : load or save to file"
  print " -c [mut%] : % of mutation"
  print " -s : use ssl"
  print " -h : help"
  print "-----------------------------------------"

def main():
  inHost = None
  outHost = None
  editor = False
  mode = None
  file = None
  sslRequired = False
  mutChance = 0
  try:
    optlist,args = getopt.getopt(sys.argv[1:],"i:o:m:f:c:hs",["in","out","mode","file","chance","help","ssl"])
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
    elif o in ("-c","--chance"):
      mutChance = int(a)
    elif o in ("-h","--help"):
      usage()
      sys.exit(2)
    elif o in ("-s","--ssl"):
      sslRequired = True
    else:
      print "error: unknown argument %s" % o
  if mode == "capture" and inHost is not None and outHost is not None and file is not None:
    capture(inHost,outHost,file,sslRequired)
  elif mode in ("replay","replayclient") and outHost is not None and file is not None:
    replayclient(outHost,file,sslRequired,mutChance)
  elif mode == "replayserver" and inHost is not None and file is not None:
    replayserver(inHost,file,sslRequired,mutChance)
  elif mode == "edit":
    e = conversationEditor(file)
  else:
    usage()
    sys.exit(0)

if __name__ == "__main__":
  main()
