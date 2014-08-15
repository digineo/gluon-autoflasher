#!/bin/bash -e
#
# Lädt die Images herunter
#

source ./config

wget \
  --mirror \
  --no-parent \
  -A "$fw_pattern" \
  $fw_base_url
