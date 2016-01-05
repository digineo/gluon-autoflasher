# coding: utf-8
import os
import re
import requests
from HTMLParser import HTMLParser
from sys import stdin

from . import *

def all():
  val = getConfig('authorized_keys')
  if val != "":
    with open(val, 'r') as f:
      uploadKeys(f.read())

  wizard()

def uploadKeys(keys):
  payload  = {'cbi.submit': 1, 'cbid.system._keys._data': keys}
  response = requests.post("http://192.168.1.1/cgi-bin/luci/admin/remote", data=payload)
  checkResponse(response)

def wizard():
  response = requests.get("http://192.168.1.1/cgi-bin/luci")
  defaults = dict(re.compile('<input .* name="([^"]+)".* value="([^"]*)"').findall(response.text))
  data     = {
    "cbi.submit":                 1,
    "cbi.cbe.wizard.1._meshvpn":  1,
    "cbi.cbe.wizard.1._location": 1,
    "cbid.wizard.1._contact":     readInput("contact", getConfig('contact', default=defaults['cbid.wizard.1._contact'])),
    "cbid.wizard.1._hostname":    readInput("hostname", defaults['cbid.wizard.1._hostname']),
    "cbid.wizard.1._meshvpn":     readBool("meshvpn", getConfig('meshvpn')),
  }

  # Traffic shaping
  if data["cbid.wizard.1._meshvpn"] in [1,"1"]:
    data["cbid.wizard.1._limit_enabled"] = readBool("limit bandwith", getConfig("limit.enabled"))

  # send request
  response = requests.post("http://192.168.1.1/cgi-bin/luci", data=data, headers={"referer": "http://192.168.1.1/cgi-bin/luci"})

  # everthing all right?
  checkResponse(response)
  if "rebooting" not in response.text:
    print RuntimeError("unexpected response: %" % response.text)

  print "rebooting"


def readBool(text, default):
  while True:
    value = raw_input("%s [%s]:" % (text, "Y/n" if default else "y/N"))
    if value=="":
      return (1 if default else 0)
    if value=="y":
      return 1
    if value=="n":
      return 0

def readInput(text, default):
  value = raw_input("%s [%s]: " % (text, default))
  if value=="":
    value = default
  return value

def checkResponse(response):
  if response.status_code != requests.codes.ok:
    response.raise_for_status()

def getConfig(keys, default=""):
  val = config.get("setup")
  for key in keys.split("."):
    if val in [default, "", None]:
      break
    val = val.get(key, default)
  return val
