#!/usr/bin/python

import random
import copy
import re

# to know that the path is infinite
# or to walk that path alone?

class socketMessage:
  DIRECTION_FORWARD = 1
  DIRECTION_BACK = 2
  MUTATE_REPEAT = 0
  MUTATE_DELETE = 1
  MUTATE_REPLACE = 2

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
