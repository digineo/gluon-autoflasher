# Automatisches Flashen von Routern

Diese Skripte sind für **Freifunk Paderborn** angepasst. Die benötigte Firmware wird automatisch von der Webseite falls diese nicht bereits im Unterverzeichnis "images" liegt.

## Benutzung

Konfiguration:

* **config** enthält die Adresse zum Download der Images, sowie die zu installierende Version.

Es gibt zwei Skripte:

* **autoflash.sh** versucht einen original TP-Link Router zu erkennen. Sobald dieser identifiziert werden konnte wird die neue Firmware automatisch installiert und nach Abschluss das Skript beendet.
* **massflash.sh** ruft *autoflash.sh* in einer Schleife auf und wartet jeweils auf den Anschluss eines neuen Routers.

## Voraussetzungen

* Der Autoflasher ist ein bash-Skript, benötigt also entweder Linux oder Cygwin auf Windows (andere Systeme mit bash-Support gehen natürlich auch).
* Der Computer muss seine Adresse per DHCP erhalten (oder in allen benötigten Subnetzen eine statische IP mit passendem Routing haben). Die Übernahme des Default-Gateways ist nicht notwendig.

