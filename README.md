pyPortProber
============

A small utility to try and determine if ports are being filtered or blocked.

##Usage

```
prober.py [-h] (--server | --client) [--host HOST [HOST ...]] --ports
                 PORTS [PORTS ...]

A utility to test port blocking or utilization.

optional arguments:
  -h, --help            show this help message and exit
  --server              Act as a server.
  --client              Act as a client.
  --host HOST [HOST ...]
                        The target host.
  --ports PORTS [PORTS ...]
                        The target port(s).
```
