# coding: utf-8
import os
import re
import sys
import subprocess
import yaml
import random
import requests

import __builtin__

FNULL    = open(os.devnull, 'w')
baseDir  = os.path.join(os.path.dirname(__file__), "../..")

def loadYAML(path):
  with open(os.path.join(baseDir, path), 'r') as f:
    return yaml.load(f)


class InvalidModel(Exception): pass
class UnknownModel(InvalidModel): pass
class UnsupportedModel(InvalidModel): pass

# Load config
__builtin__.config = loadYAML("config.yml")

# Writes output and flushes the buffer
def write(str):
  sys.stdout.write(str)
  sys.stdout.flush()

# Waits for a host to respond to ICMP echo requests
def waitForPing(address):
  write("Waiting for %s ..." % address)
  while 0 != subprocess.call(["ping","-c", "1", "-W", "1", address], stdout=FNULL):
    write('.')
  print " ✓"
