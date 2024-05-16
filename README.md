## Introduction
This repository contains samples for EXD vData SDK for Python package (exceeddata-sdk-vdata).  vData is an edge database running on vehicles' domain controllers.  It stores signal data in a high-compression file format with the extension of .vsw.  EXD vData SDK offers vsw decoding capabilities in standard programming languages such as C++, Java, Python, Javascript, and etc.  

The following sections demonstrates how to install and use the SDK.

* [System Requirement](#system-requirement)
* [Additional Dependencies](#additional-dependencies)
* [License](#license)
* [Installation](#installation)
* [API Specification](#api-specification)
* [Sample Usage](#sample-usage)
* [Full Examples](#full-examples)
  * [Convert VSW to ASC Format](#convert-vsw-to-asc-format)
  * [Convert VSW to BLF Format](#convert-vsw-to-blf-format)

## System Requirement
* python3 
* pip3

## Additional Dependencies
The following dependencies will be installed by the SDK if not already exists.
* python-snappy
* zstd

## License
The codes in the repository are released with [MIT License](LICENSE).

## Installation
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

## API specification
Publicly available SDK classes and methods are at [API Specification](https://htmlpreview.github.io/?https://github.com/exceeddata/sdk-vdata-python/blob/main/api.html).

## Sample Usage
SDK is very easy to use, in most cases 7 lines of code is sufficient.

```py
from exceeddata.sdk.vdata import VDataReaderFactory
import pandas as _pd

signals = ""  # provide a comma-separated list to select signals as needed, empty list means all signals are selected.
file = open(inputPath, "rb") 
factory = VDataReaderFactory() 
factory.setDataReaders(file)
factory.setSignals(signals)
reader = factory.open() 
frame = reader.df()
df = _pd.DataFrame(frame.objects(), columns=frame.cols(True))  # objects() return a n x m array of rows and columns, here we load into a pandas Data Frame
...
file.close()
```


## Full Examples
### Convert VSW to ASC Format
[ASCII Logging Files (.ASC)](https://support.vector.com/kb?id=kb_article_view&sysparm_article=KB0011536)  is an industry-stand Message-based format for reading and writing signal data. See [vsw2asc.py](vsw2asc.py) for a quick example on conversion.

### Convert VSW to BLF Format
[Binary Logging File (.BLF)](https://support.vector.com/kb?id=kb_article_view&sysparm_article=KB0011536)  is an industry-stand Message-based format for reading and writing signal data. See [vsw2blf.py](vsw2blf.py) for a quick example on conversion.

