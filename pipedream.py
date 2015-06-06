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

def prettyPrint(i,d,message):
  meow = ""
  if d == socketConversation.DIRECTION_FORWARD:
    print " [ message %4d -> len:0x%08x ]" % (i,len(message))
  else:
    print " [ message %4d <- len:0x%08d ]" % (i,len(message))
  print " [",
  # totalLength = len(message) % 8
  for i in range(0,len(message)):
    if i != 0 and i % 8 == 0:
      print " %s ]\n [" % meow,
      meow = ""
    elif i != 0 and i % 4 == 0:
      print "-",
    print "%02x" %  int(ord(message[i])),
    if message[i] in string.printable and message[i] != '\r' and message[i] != '\n':
      meow += message[i]
    else:
      meow += "."
  i += 1
  while i % 8 != 0:
    if i != 0 and i % 4 == 0:
      print "-",
    print "..",
    meow += "."
    i += 1
  print " %s ]" % meow

def prettyPrintShort(i,d,message):
  meow = ""
  if d == socketConversation.DIRECTION_FORWARD:
    print " [ %d -> len:0x%04x ]" % (i,len(message)),
  else:
    print " [ %d <- len:0x%04x ]" % (i,len(message)),
  print " [",
  for i in range(0,len(message)):
    if i != 0 and i % 8 == 0:
      print ""
    print "%02x" %  int(ord(message[i])),
    if message[i] in string.printable and message[i] != '\r' and message[i] != '\n':
      meow += message[i]
    else:
      meow += "."
    if i == 7:
      break
  while i % 7 != 0:
    if i != 0 and i % 4 == 0:
      print "-",
    print "..",
    meow += "."
    i += 1
  print " %s ]" % meow

def printSelection(m,row,column):
  meow = ""
  startI = row * 8
  maxI = startI + 8
  print " [",
  for i in range(startI,maxI):
    if i >= len(m):
      print "..",
      meow += "."
    else:
      if i % 8 == column:
        print "[%02x]" % ord(m[i]),
      else:
        print "%02x" % ord(m[i]),
      if m[i] in string.printable and m[i] != '\r' and m[i] != '\n':
        meow += m[i]
      else:
        meow += "."
  print " %s ]" % meow,

class conversationEditor:
  def __init__(self,f=None,interactive=True):
    self.selectToken = None
    self.sequence = None
    self.saveFile = None
    self.changeFlag = False
    print "---------------------------------------------------------------"
    self.help()
    print "---------------------------------------------------------------"
    if f:
      self.sequence = socketConversation(f)
      self.saveFile = f
    if interactive:
      self.editShell()

  def printConversation(self):
    if self.sequence is None:
      print "[err: sequence not loaded]"
      return
    else:
      for i in range(0,len(self.sequence.messages)):
        self.sequence.messages[i].prettyPrintShort(i)
        #(d,m) = self.sequence.fetchMessage(i)
        #prettyPrintShort(i,d,m)

  def editPacketHelp(self):
    print " q: quit, without save"
    print " g: quit, with save (not to file)"
    print " w/s/a/d: control cursor"
    print " x [byte]: overwrite byte"
    print " +: move byte forward"
    print " -: move byte backward"

  # edit packet
  def editPacket(self,packet):
    try:
      (d,m) = self.sequence.fetchMessage(packet)
    except:
      print " [err: could not load %d]" % packet
      return
    print "---------------------------------------------------------------"
    self.editPacketHelp()
    print "---------------------------------------------------------------"
    continueFlag = True
    selectedColumn = 0
    selectedRow = 0
    maxRow = len(m) / 8 # max row counted from 0
    while continueFlag:
      printSelection(m,selectedRow,selectedColumn)
      q = raw_input(": ").rstrip().lstrip()
      commandTokens = q.split(" ")
      c = commandTokens[0]
      if c in ("q","quit"):
        continueFlag = False
      elif c in ("h","help"):
        self.editPacketHelp()
      elif c in ("+","-"):
        cPos = selectedRow * 8 + selectedColumn
        if c == "+" and cPos < len(m) - 1:
          temp1 = m[cPos]
          temp2 = m[cPos + 1]
          m[cPos] = temp2
          m[cPos + 1] = temp1
        elif c == "-" and cPos > 0:
          temp1 = m[cPos]
          temp2 = m[cPos - 1]
          m[cPos] = temp2
          m[cPos - 1] = temp1
      elif c in ("w","s"):
        if c == "w" and selectedRow > 0:
          selectedRow -= 1
        elif c == "s" and selectedRow < maxRow:
          selectedRow += 1
        selectedColumn = 0
      elif c in ("a","d"):
        if c == "a" and selectedColumn > 0:
          selectedColumn -= 1
        elif c == "d" and selectedColumn < 7 and (selectedRow * 8 + selectedColumn < len(m) - 1): # 8 width, so 6->7 is the last 'd' command
          selectedColumn += 1
      elif c == "g":
        self.sequence.saveMessage(packet,(d,m))
        self.changeFlag = True
        continueFlag = False
      elif c == "x" and len(commandTokens) == 2 and len(commandTokens[1]) == 2:
        tempM = bytearray(m)
        tempM[selectedRow * 8 + selectedColumn] = chr( int(commandTokens[1],16) )
        m = str(tempM)

  def help(self):
    print " q: quit"
    print " p [all | num] : print sequence / packet"
    print " l [file]: load from file"
    print " h: print help message"
    print " s [num] : select a message"
    print " f: flip selected packet"
    print " d: delete selected packet"
    print " e: edit selected packet"
    print " x [file]: export packet to file"
    print " i [file]: import packet from file"
    print " set python [file?]: bind python mutation code to packet"
    print " set python None: remove python mutation code from packet"
    print " bind [regexp]: bind words to server responses"
    print " save: [file?] save sequence to file (or current file)"
    print " -: move current selection backward"
    print " +: move current selection forward"

  def editShell(self):
    continueFlag = True
    while continueFlag:
      if self.changeFlag is True:
        print " *",
      if self.selectToken is None:
        q = raw_input(" [####] : ").rstrip().lstrip()
      else:
        q = raw_input(" [%4d] : " % self.selectToken).rstrip().lstrip()
      commandTokens = q.split(" ")
      c = commandTokens[0]
      if c in ("q","quit"):
        continueFlag = False
      elif c in ("p","print"):
        if len(commandTokens) == 1:
          if self.selectToken is None:
            self.printConversation()
          else:
            (d,m) = self.sequence.fetchMessage(self.selectToken)
            prettyPrint(self.selectToken,d,m)
        elif len(commandTokens) == 2:
          if commandTokens[1] in ("a","all"):
            self.printConversation()
          else:
            i = int(commandTokens[1])
            try:
              (d,m) = self.sequence.fetchMessage(i)
              prettyPrint(i,d,m)
            except:
              print " [err: could not fetch message %d]" % i
      elif c in ("s","select") and len(commandTokens) == 2:
        try:
          self.selectToken = int(commandTokens[1])
          if self.selectToken > len(self.sequence.messages):
            self.selectToken = None
        except:
          self.selectToken = None
      elif c in ("s","select") and len(commandTokens) == 1:
        self.selectToken = None
      # elif c in ("m","mutate") and self.selectToken is not None:
      #   sm = self.sequence.messages[self.selectToken].mutate()
      #   print sm
      elif c in ("f","flip") and self.selectToken is not None:
        try:
          (d,m) = self.sequence.fetchMessage[self.selectToken]
          self.sequence.setMessage(self.selectToken,(2 - d + 1, m))
          self.changeFlag = True
        except:
          print " [err: could not fetch message %d]" % self.selectToken
      elif c in ("d","del","delete","rm"):
        try:
          del self.sequence.messages[self.selectToken]
          if self.selectToken > len(self.sequence.messages):
            self.selectToken = None
          self.changeFlag = True
        except:
          print " [err: could not delete message %d]" % self.selectToken
        if self.selectToken > len(self.sequence.messages) - 1:
          self.selectToken = None
      elif c in ("l","load") and len(commandTokens) == 2:
        self.sequence = socketConversation(commandTokens[1])
        self.saveFile = commandTokens[1]
      elif c == "save":
        if len(commandTokens) == 2:
          self.sequence.saveToFile(commandTokens[1])
        elif self.saveFile is not None:
          self.sequence.saveToFile(self.saveFile)
        self.changeFlag = False
      elif c == "set" and len(commandTokens) > 2 and self.selectToken is not None:
        if commandTokens[1] == "python" and len(commandTokens) == 3:
          if commandTokens[2] == "None":
            self.sequence.messages[self.selectToken].delPython()
          else:
            self.sequence.messages[self.selectToken].setPython(commandTokens[1])
        elif commandTokens[i] == "mandatory" and len(commandTokens) == 3:
          if commandTokens[2] == "yes":
            self.sequence.messages[self.selectToken].setMandatory(True)
          elif commandTokens[2] == "no":
            self.sequence.messages[self.selectToken].setMandatory(False)

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
