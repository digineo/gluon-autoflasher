Gluon Autoflasher
=================

*Use at your own risk!*


## Compatibility

It has been tested with:
* TP-Link Archer C7 v2 (Firmware 150427)
* TP-Link TL-WR741ND V4 (Firmware 130524, 140410 and 150119)
* TP-Link TL-WR841N V8 (Firmware 130506 and 140724)
* TP-Link TL-WR841N V9 (Firmware 150104 and 150310)
* TP-Link TL-WR841N V10 (Firmware 150310 and 150616)
* TP-Link TL-WDR3600 v1 (Firmware 130909, 141022, 150302 and 150518)
* TP-Link TL-WDR4300 v1 (Firmware 141113, 150302 and 150518)
* TP-Link TL-WDR4900 v1 (Firmware 130424)
* TP-Link TL-WR1043ND v1 (Firmware 130428 and 140319)
* TP-Link TL-WR1043ND v2 (Firmware 140912, 150717 and 150910)


## Requirements

The following packages have to be installed on the system:

### Debian/Ubuntu

```
apt-get install python-requests
```

### OS X

```
pip install requests
```


## Usage

Ensure your ethernet interface has addresses in the networks 192.168.0.0/24 and 192.168.1.0/24.
Assuming your interface is `eth0` then you run on Linux as root:
```
ip addr add 192.168.0.2/24 dev eth0
ip addr add 192.168.1.2/24 dev eth0
```

Copy the `config.yml.default` to `config.yml` and adapt it to your needs.

Then start the autoflasher with:

```
./autoflash
```


## License

This project is licensed under the terms of the AGPL license.
