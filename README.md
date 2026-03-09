# kbib_lib

Python lib for forming bibliography.

# Docs

Coming soon... mb

# Run

## from pip

```bash
pip3 install kbib_lib
kbib_lib ../examples/2.yaml /path/to/out.txt
# or better use funcs from `from kbib_lib import *` for your needs
```

## from this repo

```bash
python -m venv venv
source venv/bin/activate
pip3 install --upgrade pip
pip3 install -r req.txt

cd src
python3 -m kbib_lib ../examples/2.yaml /path/to/out.txt
```
