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
import gluon
import gluon.flasher
import gluon.models
import os

modelsDirectory = "models"


class TestAuthorization(unittest2.TestCase):

  def get_authorization(self, basename):
    return gluon.flasher.getAuthorization(open("login/%s.html" % basename,'r').read())

  def test_unsupported(self):
    with self.assertRaises(gluon.UnsupportedModel):
      self.get_authorization("unsupported")

  def test_wdr3600_150518(self):
    self.assertEqual(('hex_md5', 'save'), self.get_authorization("wdr3600_150518"))

  def test_wr1043v1_130428(self):
    self.assertEqual(('base64', 'root'), self.get_authorization("wr1043nd-v1_130428"))

  def test_wr1043v1_150518(self):
    self.assertEqual(('base64', 'root'), self.get_authorization("wr1043nd-v1_150518"))

  def test_wr1043v2_130428(self):
    self.assertEqual(('hex_md5', 'save'), self.get_authorization("wr1043-v2_150707"))


# Empty class
class TestModels(unittest2.TestCase): pass


def getModel(filename):
  with open("%s/%s" % (modelsDirectory, filename),'r') as f:
    return gluon.models.extract(f.read())

def create_test(filename, model):
  def f(self):
    if model=="unknown":
      # special case
      with self.assertRaises(gluon.UnknownModel):
        getModel(filename)
    elif model=="unsupported":
      # special case
      with self.assertRaises(gluon.UnsupportedModel):
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
