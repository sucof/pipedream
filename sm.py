#!/usr/bin/python

import random
import copy
import re
import pickle
import string

# to know that the path is infinite
# or to walk that path alone?

VERSION="I AM SUN OF HOUSE ARISUN - AND I AM INVINCIBLE"

class socketMessage:
  DIRECTION_FORWARD = 1
  DIRECTION_BACK = 2
  MUTATE_REPEAT = 0
  MUTATE_DELETE = 1
  MUTATE_DICTIONARY = 2

  def __init__(self,d,m):
    self.direction = d
    self.message = m
    self.py = None
    d = bytearray(m)
    # credit stack-overflow for building the dictionary
    chars = r"A-Za-z0-9/\-:.,_$%'()[\]<> "
    shortest_run = 4
    regexp = '[%s]{%d,}' % (chars, shortest_run)
    pattern = re.compile(regexp)
    stringsarray = re.findall(pattern,d)
    strings = []
    for string in stringsarray:
      strings.append(bytearray(string))
    self.dict = strings
    self.bindings = []
    self.py = None
    self.mandatory = False

  def setMandatory(self,i):
    self.mandatory = i

  def getMandatory(self):
    return self.mandatory

  def prettyPrintShort(self,i):
    d = self.direction
    message = self.message
    meow = ""
    woof = ""
    if len(self.bindings) > 0:
      woof += "B%d " % len(self.bindings)
    if self.py is not None:
      woof += "P "
    if self.mandatory is True:
      woof += "M "
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
    print " %s ] %s" % (meow,woof)

  def bindWord(self,word):
    self.bindings.append(re.compile(word))

  # does this response match the current binding?
  def checkBind(self,message):
    if len(self.bindings) == 0:
      return False
    for word in self.bindings:
      if word.match(message) is None:
        return False
    return True

  def setPython(self,pyfile):
    f = open(pyfile,"r")
    py = f.read()
    f.close()
    self.py = py

  def delPython(self):
    self.py = None

  def mutate(self):
    inputdict = self.dict
    if self.py == None:
      newSeed = bytearray(copy.copy(self.message))
      if len(self.dict) == 0:
        mutType = random.randint(0,1)
      else:
        mutType = random.randint(0,2)
      maxLen = len(newSeed)
      mutatePosition = random.randint(0,len(self.message))
      if mutType == socketMessage.MUTATE_REPEAT:
        newSeed = newSeed[0:mutatePosition] + bytearray(newSeed[mutatePosition]) * random.randint(0,100000) + newSeed[mutatePosition:maxLen]
      elif mutType == socketMessage.MUTATE_DELETE:
        mutateRemoveLength = random.randint(0,len(newSeed) - mutatePosition)
        del newSeed[mutatePosition:mutatePosition + mutateRemoveLength]
      elif mutType == socketMessage.MUTATE_DICTIONARY:
        newSeed = newSeed[0:mutatePosition] + random.choice(inputdict) + newSeed[mutatePosition:maxLen]
      return str(newSeed)
    else:
      exec(self.py)
      return a

class socketConversation:
  DIRECTION_FORWARD = 1
  DIRECTION_BACK = 2

  def __init__(self,f=None):
    if f is not None:
      self.loadFromFile(f)
    else:
      self.messages = []

  def loadFromFile(self,filename):
    f = open(filename,"r")
    v = f.readline().rstrip()
    global VERSION
    if v != VERSION:
      raise BaseException("[err: version mismatch]")
    else:
      cv = f.read()
      self.messages = pickle.loads(cv)
    f.close()
  
  def saveToFile(self,filename):
    f = open(filename,"w")
    global VERSION
    f.write(VERSION+"\n")
    f.write(pickle.dumps(self.messages))
    f.close()

  def appendMessage(self,direction,message):
    self.messages += [socketMessage(direction,message)]

  def fetchMessage(self,i):
    sm = self.messages[i]
    return (sm.direction,sm.message)

  def fetchMutated(self,i):
    return self.messages[i].mutate()

  def saveMessage(self,i,message):
    (d,m) = message
    self.messages[i] = socketMessage(d,m)
