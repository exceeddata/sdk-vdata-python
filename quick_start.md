# 快速上手

# 环境需求
Python3 
Pip3

还需要安装
python-snappy, zstd

# 安装
可以直接通过pip3进行安装

```
pip3 install exceeddata-sdk-vdata 

Collecting exceeddata-sdk-vdata
  Using cached exceeddata_sdk_vdata-2.8.2.2-py2.py3-none-any.whl (30 kB)

Requirement already satisfied: zstd in /opt/homebrew/lib/python3.10/site-packages (from exceeddata-sdk-vdata) (1.5.5.1)
Requirement already satisfied: python-snappy in /opt/homebrew/lib/python3.10/site-packages (from exceeddata-sdk-vdata) (0.7.1)

Requirement already satisfied: cramjam in /opt/homebrew/lib/python3.10/site-packages (from python-snappy->exceeddata-sdk-vdata) (2.8.3)

Installing collected packages: exceeddata-sdk-vdata
Successfully installed exceeddata-sdk-vdata-2.8.2.2
```

**检查是否已经安装**

```
pip3 list |grep exceeddata

exceeddata-sdk-vdata 2.8.2.2
```