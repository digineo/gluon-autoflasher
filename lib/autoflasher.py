# coding: utf-8
import os
import re
import sys
import subprocess
import yaml
import random
import requests


FNULL    = open(os.devnull, 'w')
BaseDir  = os.path.join(os.path.dirname(__file__), "..")
ImageDir = os.path.join(BaseDir, "images")
Config   = os.path.join(BaseDir, "images")

def loadYAML(path):
  with open(os.path.join(BaseDir, path), 'r') as f:
    return yaml.load(f)

# Load models
Config = loadYAML("config.yml")
Models = loadYAML("lib/models.yml")

# Writes output and flushes the buffer
def write(str):
  sys.stdout.write(str)
  sys.stdout.flush()

# Waits for a host to respond to ICMP echo requests
def WaitForPing(address):
  write("Waiting for %s ..." % address)
  while 0 != subprocess.call(["ping","-c", "1", "-W", "1", address], stdout=FNULL):
    write('.')
  print " ✓"

class InvalidModel(Exception): pass
class UnknownModel(InvalidModel): pass
class UnsupportedModel(InvalidModel): pass

def ExtractModel(html):
  match = re.compile("WD?R[0-9]+N? v[0-9]+").search(html)
  if match == None:
    raise UnknownModel("Unable to extract model information")

  model = match.group(0)
  name  = Models.get(model, None)
  if name != None:
    return name
  else:
    raise UnsupportedModel("Unsupported model: %s" % model)


# Returns the local path to the image
def GetImage(model):
  fwConfig = Config["firmware"]
  filename = "%s-%s.bin" % (fwConfig["prefix"], model)
  url      = "%s%s" % (fwConfig["url"], filename)
  path     = os.path.join(ImageDir, filename)

  if not os.path.exists(path):
    write("Downloading %s ..." % url)
    tmpfile  = "%s.tmp" % path

    # Do the request
    response = requests.get(url, stream=True)
    if response.status_code != requests.codes.ok:
      response.raise_for_status()

    # Save the response
    with open(tmpfile, 'wb') as f:
      for chunk in response.iter_content(chunk_size=1024*256):
        f.write(chunk)
        write(".")

    # Rename tempfile to target
    os.rename(tmpfile, path)
    print " ✓"
  return path

class AutoFlasher:
  def __init__(self, address):
    self.address = address
    self.session = requests.Session()
    self.urls = {
      "root":    "/",
      "save":    "/userRpm/LoginRpm.htm?Save=Save",
      "menu":    "/userRpm/MenuRpm.htm",
      "status":  "/userRpm/StatusRpm.htm",
      "upgrade": "/userRpm/SoftwareUpgradeRpm.htm",
      "upload":  "/incoming/Firmware.htm",
      "flash":   "/userRpm/FirmwareUpdateTemp.htm",
    }
    self.session_prefix = ''

    WaitForPing(address)

    self.authorize()

    write("Fetching model ... ")
    self.model = ExtractModel(self.request("status", "menu").text)
    print self.model

    self.image = GetImage(self.model)

    write("Uploading image ... ")
    self.request("upload", "upgrade", files={'Filename': open(self.image, 'rb')})
    print " ✓"

    write("Flashing ... ")
    self.request("flash", "upload")
    print " ✓"

    WaitForPing("192.168.1.1")

  def authorize(self):
    try:
      # newer TP-Link firmwares use cookie authentication
      html = self.request("root", "root").text
      if "loginBox" not in html:
        raise RuntimeError("unexpected html page")

      # store credentials in cookie
      self.session.cookies.set("Authorization", "Basic%20YWRtaW46MjEyMzJmMjk3YTU3YTVhNzQzODk0YTBlNGE4MDFmYzM%3D")

      # get session ID
      html  = self.request("save", "root").text
      match = re.compile('http://192.168.0.1/([0-9A-Z]+)/userRpm/').search(html)
      if match == None:
        raise RuntimeError("Unable to extract session_id")

      self.session_prefix = "/" + match.group(1)

    except requests.exceptions.HTTPError:
      # old TP-Link firmware versions use basic auth (i.e. WDR3600v1 130909)
      self.session.auth  = ('admin', 'admin')

  def request(self, urlType, refererType, files=None):
    url     = self.getURL(urlType)
    headers = {"referer": self.getURL(refererType)}

    # do the request
    if files == None:
      response = self.session.get(url, headers=headers)
    else:
      response = self.session.post(url, headers=headers, files=files)

    # check status code
    if response.status_code != requests.codes.ok:
      response.raise_for_status()

    return response

  def getURL(self, type):
    return "http://%s%s%s" % (self.address, self.session_prefix, self.urls[type])


def Run():
  AutoFlasher("192.168.0.1")
