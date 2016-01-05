# coding: utf-8
import re
import requests

from . import *
import gluon.models as models

# shorthand method
def run(address):
  Flasher(address).run()

# Determines the authorization method and URI
def getAuthorization(html):
  if "loginBox" not in html:
    raise UnsupportedModel("unexpected html page")

  if "hex_md5" in html:
    method = "hex_md5"
  elif "Base64Encoding" in html:
    method = "base64"
  else:
    raise UnsupportedModel("unsupported login page")

  if "LoginRpm.htm" in html:
    uri = 'save'
  else:
    uri = 'root'

  return (method,uri)


class Flasher:
  def __init__(self, address):
    self.address = address
    self.session = requests.Session()
    self.authValues = {
      'hex_md5': "Basic%20YWRtaW46MjEyMzJmMjk3YTU3YTVhNzQzODk0YTBlNGE4MDFmYzM%3D",
      'base64':  "Basic%20YWRtaW46YWRtaW4%3D",
    }
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

  def run(self):
    waitForPing(self.address)

    self.authenticate()

    write("Fetching model ... ")
    self.model = models.extract(self.request("status", "menu").text)
    print self.model

    self.image = models.get(self.model)

    write("Uploading image ... ")
    self.request("upload", "upgrade", files={'Filename': open(self.image, 'rb')})
    print " ✓"

    write("Flashing ... ")
    self.request("flash", "upload")
    print " ✓"

    waitForPing("192.168.1.1")

  def authenticate(self):
    try:
      # newer TP-Link firmwares use cookie authentication
      html = self.request("root", "root").text

      auth, uri = getAuthorization(html)

      # store credentials in cookie
      self.session.cookies.set("Authorization", self.authValues[auth])

      # let's log in
      html = self.request(uri, "root").text

      # was the login successful?
      if "loginBox" in html:
        raise UnsupportedModel("failed to authenticate")

      if uri != "root":
        # extract the session ID
        match = re.compile('http://[0-9\.]+/([0-9A-Z]+)/userRpm/').search(html)
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
