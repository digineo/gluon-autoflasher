# coding: utf-8
import os
import re
import sys
import subprocess
import urllib2, base64
import yaml
import random
import string


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
  while 0 != subprocess.call(["/bin/ping","-c", "1", "-W", "1", address], stdout=FNULL):
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
    response = urllib2.urlopen(url)
    with open(tmpfile, 'wb') as f:
      while True:
        chunk = response.read(1024*1024)
        if not chunk: break
        f.write(chunk)
        write(".")
    os.rename(tmpfile, path)
    print " ✓"
  return path

class AutoFlasher:
  def __init__(self, address):
    WaitForPing(address)
    self.address = address
    self.urls = {
      "menu":    "http://%s/userRpm/MenuRpm.htm",
      "status":  "http://%s/userRpm/StatusRpm.htm",
      "upgrade": "http://%s/userRpm/SoftwareUpgradeRpm.htm",
      "upload":  "http://%s/incoming/Firmware.htm",
      "flash":   "http://%s/userRpm/FirmwareUpdateTemp.htm",
    }

    write("Fetching model ... ")
    request    = self.createRequest("status", "menu")
    response   = urllib2.urlopen(request)
    self.model = ExtractModel(response.read())
    print self.model

    self.image = GetImage(self.model)
    write("Uploading image ... ")
    self.upload()
    print " ✓"

    write("Flashing ... ")
    self.flash()
    print " ✓"

    WaitForPing("192.168.1.1")
    print " ✓"

  def upload(self):
    data     = open(self.image, 'rb').read()
    boundary = ''.join(random.choice(string.letters) for ii in range(31))
    body     = '\r\n'.join([
      '--%s' % boundary,
      'Content-Disposition: form-data; name="Filename"; filename="firmware.bin"',
      'Content-Type: application/octet-stream',
      '',
      data,
      '--%s--' % boundary,
      ''
    ])
    request = self.createRequest("upload", "upgrade", body=body)
    request.add_header('Content-Type', 'multipart/form-data; boundary=%s' % boundary)
    request.add_header('Content-Length', str(len(body)))
    urllib2.urlopen(request)


  def flash(self):
    request = self.createRequest("flash", "upload")
    urllib2.urlopen(request)

  def createRequest(self, urlType, refererType, body=None):
    request = urllib2.Request(self.urls[urlType] % self.address, body)
    request.add_header('Authorization', b'Basic ' + base64.b64encode("admin:admin"))
    request.add_header('Referer', self.urls[refererType] % self.address)
    return request

def Run():
  AutoFlasher("192.168.0.1")
