# coding: utf-8
import os
import re
import requests

from . import *

models   = loadYAML("lib/gluon/models.yml")
imageDir = os.path.join(baseDir, "images")

# Returns the local path to the image
def get(model):
  fwConfig = config["firmware"]
  filename = "%s-%s.bin" % (fwConfig["prefix"], model)
  url      = "%s%s" % (fwConfig["url"], filename)
  path     = os.path.join(imageDir, filename)

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

# Extracts the model from the HTML code
def extract(html):
  match = re.compile("(WD?R\d+[A-Z]*|Archer C\d) v\d+").search(html)
  if match == None:
    #with open('unknown-model.html', 'w') as f:
    #  f.write(html)
    raise UnknownModel("Unable to extract model information")

  model = match.group(0)
  name  = models.get(model, None)
  if name != None:
    return name
  else:
    raise UnsupportedModel("Unsupported model: %s\nPlease add it to lib/gluon/models.yml" % model)

