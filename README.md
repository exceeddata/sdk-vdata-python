# sdk-vdata-python
This repo contains samples for EXD vData SDK for Python package (exceeddata-sdk-vdata).

# Python Requirement
* python3 
* pip3

# Additional Dependencies
The following dependencies will be installed by the SDK if not already exists.
* python-snappy
* zstd

# Installation
exceeddata-sdk-vdata package may be installed using pip command.

```sh
pip3 install exceeddata-sdk-vdata 

Collecting exceeddata-sdk-vdata
  Using cached exceeddata_sdk_vdata-2.8.2.2-py2.py3-none-any.whl (30 kB)

Requirement already satisfied: zstd in /opt/homebrew/lib/python3.10/site-packages (from exceeddata-sdk-vdata) (1.5.5.1)
Requirement already satisfied: python-snappy in /opt/homebrew/lib/python3.10/site-packages (from exceeddata-sdk-vdata) (0.7.1)

Requirement already satisfied: cramjam in /opt/homebrew/lib/python3.10/site-packages (from python-snappy->exceeddata-sdk-vdata) (2.8.3)

Installing collected packages: exceeddata-sdk-vdata
Successfully installed exceeddata-sdk-vdata-2.8.2.2
```

**Post Installation**

```sh
pip3 list |grep exceeddata

exceeddata-sdk-vdata 2.8.2.2
```
