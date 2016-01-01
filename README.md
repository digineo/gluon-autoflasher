Gluon Autoflasher
=================

*Use at your own risk!*


## Compatibility

It has been tested with:
* TP-Link TL-WDR3600 v1 (Firmware 130909 and 150518)
* TP-Link TL-WDR4300 v1 (Firmware 150518)
* TP-Link TL-WR1043ND v2 (Firmware 150717)


## Requirements

The following packages have to be installed on your system:

### Debian/Ubuntu

```
apt-get install python-requests
```

### OS X

```
pip install requests
```


## Usage

TP-Link routers with stock firmware usually have the IP address `192.168.0.1/24`.
Ensure your interface has one address in this network.
Assuming your interface is `eth0` then you run on Linux as root:
```
ip addr add 192.168.0.2/24 dev eth0
```

Then you start the autoflasher with:

```
./autoflash
```


## License

This project is licensed under the terms of the AGPL license.
