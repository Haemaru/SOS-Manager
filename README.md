SOS-Manager
---

This project is role and password manager of [SOS](https://github.com/Luavis/SOS) which is security module in linux.

### Dependency

1. python-dev: install it by apt-get or yum
2. [SOS](https://github.com/Luavis/SOS) module

### How to install

1. Use setup.py
```
  python setup.py install
```

### How to use

```
Usage: sos_manager [-h] mode options

positional arguments:
  mode:     login | logout | reload | manager | encrypt | unlock | lock | passwd

optional arguments:
  -h, --help  show help message
  --options options  options depned on mode
