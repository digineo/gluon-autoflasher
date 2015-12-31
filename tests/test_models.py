#!/usr/bin/env python2
#
# Requirements:
# apt-get install python-unittest2
#
# Run with:
# unit2 discover
#

from sys import path
path.append("../lib")

import unittest2
import autoflasher
import os

modelsDirectory = "models"

def getModel(filename):
  with open("%s/%s" % (modelsDirectory, filename),'r') as f:
    return autoflasher.ExtractModel(f.read())

# Empty class
class TestModels(unittest2.TestCase): pass

def create_test(filename, model):
  def f(self):
    if model=="unknown":
      # special case
      with self.assertRaises(autoflasher.UnknownModel):
        getModel(filename)
    elif model=="unsupported":
      # special case
      with self.assertRaises(autoflasher.UnsupportedModel):
        getModel(filename)
    else:
      # supported device
      self.assertEqual(getModel(filename), model)
  return f

# Generate test methods
for filename in os.listdir(modelsDirectory):
  basename = os.path.splitext(filename)[0]
  model    = basename.split("_")[0]

  test_method = create_test(filename, model)
  test_method.__name__ = 'test_%s' % basename
  setattr(TestModels, test_method.__name__, test_method)
