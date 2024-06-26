# 介绍
本代码库包含EXD vData SDK for Python package (exceeddata-sdk-vdata)的使用示例.  EXD vData SDK 支持多种编程语言，包括 C++, [Java](https://github.com/exceeddata/sdk-vdata-java), [Python](https://github.com/exceeddata/sdk-vdata-python), [Javascript](https://github.com/exceeddata/sdk-vdata-javascript), 等等.  

英文版的README在[here](README.md).

## 目录
- [系统要求](#系统要求)
- [安装依赖](#安装依赖)
- [代码授权](#代码授权)
- [安装步骤](#安装步骤)
- [API文档](#api文档)
- [背景介绍](#背景介绍)
  - [车端信号](#车端信号)
  - [数据转换与矩阵](#数据转换与矩阵)
  - [常用的车端信号存储的文件格式](#常用的车端信号存储的文件格式)
- [数据的填充降频与采样](#数据的填充降频与采样)
  - [只填充](#只填充)
  - [填充与填充时间简隔](#填充与填充时间简隔)
  - [Objects方法与降频](#objects方法与降频)
- [SDK使用](#SDK使用)
  - [基础场景](#基础场景)
    - [SDK读入解析数据](#sdk读入解析数据)
    - [将数据导出成CSV](#将数据导出成csv)
    - [筛选信号解析](#筛选信号解析)
  - [高级场景](#高级场景)
    - [时间过滤](#时间过滤)
    - [多文件合并解析](#多文件合并解析)
    - [降频到1秒](#降频到1秒)
- [完整代码示例](#完整代码示例)
  - [VSW解析应用](#vsw解析应用)
  - [VSW转ASC格式](#vsw转asc格式)
  - [VSW转BLF格式](#vsw转blf格式)
- [示例数据文件](#示例数据文件)
- [获得帮助](#获得帮助)
- [贡献代码](#贡献代码)

# 系统要求
- python3 
- pip3

# 安装依赖
SDK将会需要安装以下的依赖库.
- python-snappy
- zstd

# 代码授权
本代码库内的代码为[MIT License](LICENSE)授权.

# 安装步骤
最新SDK的安装包在[Python Package Index (PyPI)](https://pypi.org/project/exceeddata-sdk-vdata)， 可以使用pip命令安装。

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

**安装后**

```sh
pip3 list |grep exceeddata

exceeddata-sdk-vdata 2.8.2.2
```

# API文档
SDK的对象类的方法文档在[API文档](https://htmlpreview.github.io/?https://github.com/exceeddata/sdk-vdata-python/blob/main/doc/api.html).

# 背景介绍

## 车端信号

车端的信号与我们云端常用的数据库其实并不相同。在云端的数据处理时，我们经常用二维表的方式来思考问题，习惯性把车辆的信号结果数据当成一张二维的表格来处理数据。而事实上，车端的信号数据以CAN总线为列，都是按时间，信号帧的形式出现的。
TimeStamp | Channel | FrameId | Data ||
:-: | :-: | :-: | :-: | :-:
| 0.522000000 | 14 | 1FFABC10 | 00 00 00 00 78 20 81 C6 |
| 0.522000000 | 14 | 1FFABC11 | 00 00 00 00 00 00 00 00 |
| 0.530000000 | 0 | 11 | C1 00 00 FF FF FF FF FF |
| 0.530000000 | 2 | 10 | 81 1F 00 40 78 24 83 C6 |
| 0.562000000 | 14 | 1FFABC10 | 00 00 00 00 78 20 81 C6 |
| 0.562000000 | 14 | 1FFABC11 | 00 00 00 00 00 00 00 00 |

上表是一个车端的CAN数据的一个简单的示例，时间单位是秒，在Data部分里记录的是报文内容。这个示例里只关注了信号的一些基础的信号值信息，其余还有一些其他的信息，如方向等，暂时不在上表中展示。

上述的表格，如果转换成我们常见的平铺的二维数组的形式来理解，通常是这样的形式：

TimeStamp | 14_0x1FFABC10 | 14_0x1FFABC11 | 0_0x0 | 2_0x10 
:-: | :-: | :-: | :-: | :-:
| 0.522000000 | 00 00 00 00 78 20 81 C6 | 00 00 00 00 00 00 00 00 | | |
| 0.530000000 |  |  | C1 00 00 FF FF FF FF FF | 81 1F 00 40 78 24 83 C6 |
| 0.562000000 | 00 00 00 00 78 20 81 C6 | 00 00 00 00 00 00 00 00 | | |

其中，我们总线和报文ID的转换成列名以{Channel_id}_{Frame_id}的形式命名。

在一个真实的车上，如果以报文计，通常会和数百组或数千组不同的报文；若以报文中的解析出的属性计，通常会有数千甚至上万不同的属性。因此，车端的信号很难用传统的大宽表来存储数据。如果全部展开，人也很难阅读。

## 数据转换与矩阵
通常一个信号帧长度从8Bytes到64Bytes不等。如果要将总线上的报文解析成可阅读的数据值，则还需要通信矩阵中的相应信息才能进行转换。
矩阵中的信息包括：开始位置，信号长度，编码方式（MOTOROLA/Intel)，倍数，偏移量等信息。通过矩阵的转换，总线上的报文可以非常高效的表达各种数值。
以室内外为例：如果我们用浮点数来表达温度，则至少要占用32bit。假设我们现在温度表达范围是-40-+60摄氏度，精度为0.1度。如果我们以用矩阵来配合来表示温度，则可以只用10bit。 10bit的无符号整数的范围是0-1023，矩阵中倍数可以用0.1，偏移量用-40。 当总线上的10个bit值为0是，转换成INT为0，实际表达的温度即为0.1* 0+(-40) = -40度；当总上上传 0x01 FF时，10进制数据为511，表示的温度为511*0.1+（-40） =11.1度。

## 常用的车端信号存储的文件格式

[常用文件格式说明](http://www.smartsct.com/page10?article_id=49)

- ASC： 以信号报文为单位组织数据，整体以文本方式呈现。如果有DBC文件，人类可以凭借计算器计算相应的值。

- BLF： 以信号报文为单位组织数据，以二进制放置在日志容器对象中，可以压缩。因此，若打开压缩，BLF人类不可阅读和解析。外部转换工具也需要DBC文件才可以解析。

- MDF： 以信号报文或MDF专有对象组织数据。可压缩。已经将矩阵信息存储在文件中。可以直接用外部转换工具进行转换。

- CSV： 文本的，以行列方式组织数据，若数据量少，可以直接阅读。超有数百列以上，即使有工具支持，也很难。

- VSW： EXD特有的专用格式。以时间块，信号块等二个维度组织数据，支持块内压缩。

# 数据的填充降频与采样
场景说明：由于车端数据的复杂性，车端的信号有常规按不同的频率上报的，如有100HZ，20HZ，10HZ的，也有事件触发型的。数据平铺之后是一个非常稀疏的矩阵（二维数组），如果时间精度又在微秒的话，通常这个矩阵每一行只有2-3列是有数据的，即第一行的时间列，后面通常只有一个信号列有数据，偶尔有两个信号同时在微秒级有数据。
以下列数据为例：
timestamp.ms | signal_50hz | signal_20hz | signal_10hz 
:-: | :-: | :-: | :-: 
1010 | 1 | |
1011 |  | 201 |
1020 | 2 | |
1030 | 3 | |
1040 | 4 | |
1045 | |  | 1001
1050 | 5 | |
1060 | 6 | | 
1061 |  | 202 |
1070 | 7 | |
1080 | 8 | |
1090 | 9 | |
1100 | 10 | |
1101 |  | 203 |
1110 | 11 | |
1120 | 12 | |
1130 | 13 | |
1140 | 14 | |
1145 | |  | 1002
1150 | 15 | |
1160 | 16 | | 
1161 |  | 204 |
1170 | 17 | |
1180 | 18 | |
1190 | 19 | |
1200 | 20 | |
1201 |  | 205 |
1210 | 21 | |
1220 | 22 | |
1230 | 23 | |
1240 | 24 | |
1245 | |  | 1003
1250 | 25 | |
1260 | 26 | |
1261 |  | 206 | 
1270 | 27 | |
1280 | 28 | |
1290 | 29 | |
1300 | 30 | |

## 只填充
densifyRowsAhead>5
densifyOutputItv=0;
如果只是进行填充的，且往后查找行数足够的话，则会产生如下的输出：
timestamp.ms | signal_100hz | signal_20hz | signal_10hz 
:-: | :-: | :-: | :-: 
1010 | 1 | 201 | 1001
1011 | 1 | 201 | 1001
1020 | 2 | 201 | 1001
1030 | 3 | 201 | 1001
1040 | 4 | 201 | 1001
1045 | 4 | 201 | 1001
1050 | 5 | 201 | 1001
1060 | 6 | 201 | 1001
1061 | 6 | 202 | 1001
1070 | 7 | 202 | 1001
1080 | 8 | 202 | 1001
1090 | 9 | 202 | 1001
1100 | 10 | 202 | 1001
1101 | 10 | 203 | 1001
1110 | 11 | 203 | 1001
1120 | 12 | 203 | 1001
1130 | 13 | 203 | 1001
1140 | 14 | 203 | 1001
1145 | 14 | 203 | 1002
1150 | 15 | 203 | 1002
1160 | 16 | 203 | 1002
1161 | 16 | 204 | 1002
1170 | 17 | 204 | 1002
1180 | 18 | 204 | 1002
1190 | 19 | 204 | 1002
1200 | 20 | 204 | 1002
1201 | 20 | 205 | 1002
1210 | 21 | 205 | 1002
1220 | 22 | 205 | 1002
1230 | 23 | 205 | 1002
1240 | 24 | 205 | 1002
1245 | 24 | 205 | 1003
1250 | 25 | 205 | 1003
1260 | 26 | 205 | 1003
1261 | 26 | 206 | 1003
1270 | 27 | 206 | 1003
1280 | 28 | 206 | 1003
1290 | 29 | 206 | 1003
1300 | 30 | 206 | 1003

## 填充与填充时间简隔
densifyOutputItv参数的意义为重新采样的时间间隔，单位为毫秒。
即，如果指定为100，则输出为10HZ数据，如果指定的时间范围内有多条数据，则输出最接近采样时间点的数据。
以下为例： 
densifyRowsAhead>5
densifyOutputItv=100;
timestamp.ms | signal_50hz | signal_20hz | signal_10hz 
:-: | :-: | :-: | :-: 
1100 | 10 | 202 | 1001
1200 | 20 | 204 | 1002
1300 | 30 | 206 | 1003

## Objects方法与降频
与Values方法的区别在于Obects方法并没有采用内部的Queue对数据进行缓存和排序，省略了构造内部的Queue，因此其性能会大大优于Values方法。如果输入的数据的是完全有序的，其输出结果也与values方法一致。
但如果输入数据是无序的，且在降频的同一时间有多条数据，那么，Objects与Values方法将产生不同的结果 。

给出以下的数据(只有三条，与上面的并不相同)
timestamp.ms | signal_50hz | signal_20hz | signal_10hz 
:-: | :-: | :-: | :-:
100 | 10 | 202 | 1001 
50 | 5 | 201 | 1001
150 | 15 | 203 | 1002

object1s方法的输出可能是
timestamp.ms | signal_50hz | signal_20hz | signal_10hz 
:-: | :-: | :-: | :-:
1000 | 10 | 202 | 1001 

而values(densifyOutputItv=100)则可能输出 
timestamp.ms | signal_50hz | signal_20hz | signal_10hz 
:-: | :-: | :-: | :-:
1000 | 15 | 203 | 1002

注：values针对时间进行排序后， 0.050s的数据在第一行； object1s未排序， 0.100s的数据在第一条。


# SDK使用
SDK提供了多个不同的函数接口和参数，用于将VSW中存储的信号或报文以二维数组的形式返回给应用。在数据读取的同时， SDK还支持数据填充，采样降频等多种操作。


## 基础场景
### SDK读入解析数据
1. 读入数据，构建Seekable对象
通常VSW的输入来自于文件或者已经在内存中的Byte数组，每种SDK都有不同的读入对象。

2. 通过VDataReaderFactory构造VDataReader
由于VDataReader对应的参数较多，因此SDK提供了工厂模式构建VDataReader对象。
这一步的主要设置参数有：

*Seekables*：如果有多个文件需要合并解析，可以一起作为参数传入给VDataReaderFactory。

columnExpandMode: 列展开的模式。仅对于数据中有Struct等复杂数据类型的情况下适用。列展开模式有：None, Flat, Full。详细说明见后续的数据类型章节。

signals：信号清单，支持通配符

signalQueueMode: 信号队列模式，支持all，first，last三种模式。仅在values或迭代器处理中有效。意义是当VSW中的数据有毫秒级的数据重复时，输出何种数据。all，指全部输出；first和last分别指输出第一条和最后一条。如果数据中没有毫秒级的重复数据，此参数没有实际作用。

applyFormula：是否使用公式。仅针对于在VSW存储了公式的信号有效，缺省值为true。如果信号在VSW存储了公式，当为True时，输出是套用公式后的结果；为False时，输出的是实际存储的数据。

queryStartTime/queryEndTime： 数据的开始时间，结束时间。


3. 调用VDataFrame获取数据，并对数据进行处理
SDK提供了values/objects两个函数将VSW中的数据全部转换成行列数据，另外也提供了迭代器面向内存敏感型的客户。几种方法各有不同的优点，面向不同的应用场景。
values提供了按时间排序后的数据输出，但因为需要排序，所以相对速度较慢。如果输出信号数非常大的情况下，CPU开销较大，也需要较多的内存来缓存数据。
objects接口提供了原始的数据输出，数据顺序与VSW中写入顺序一致。因为不需要排序，只需要按时间对齐，是处理性能最优的接口。

### 将数据导出成CSV
从2.8.1开始，VDataFrame在原有iterator()的增加提供 objects()，object1s()，sampling()的数据解析实现。但因为这些新接口有一系列改动，建议使用2.8.3+以后的稳定接口。这几种解析方法的区别如下：

●iterator() - VDataFrame一直以来都支持的流式解析接口。这个接口支持大数据量的解析。不论VDataReader读入时一共解析多少个数据文件，iterator()使用的内存消耗大约为读入一个数据文件内并解压一个时间切片内的数据所占的缓冲内存。iterator() 对所有的数据进行流式排序并逐条输出, 所以它占用的CPU相对高并耗时相对长。
oVDataFrame的iterator()接口只限java sdk开放
o在javascript和python sdk里，VDataFrame提供values()接口（类似pandas DataFrame的values）， values()的实现为iterator()的实现步骤，但返回是全数据行的array对象。

●objects() - 对最经常使用的解析场景（例：单个数据文件的解析），objects()提供性能优化的解析实现。 objects()的大概实现原理是在内存里建立一个时间x信号列的矩阵，并将所有数据按时间index插入这个矩阵，最后输出全数据行的array对象。用空间换CPU和时间，objects()使用的内存是读入并解压后的全部数据量，所以建议解析前10MB以下的总数据文件大小用objects()，大于这个量的继续用iterator()流式接口。

●sampling() - 对降频解析场景（例：从高精数据里提取降频数据用于TSP平台数据展示或BI报告），sampling()提供性能优化的降频解析实现。如果解析全部高精数据再逐条降频，大量CPU会消耗在最终没有用到的数值上。 所以sampling()的大概实现原理是在内存里建立一个降频后的时间x信号列的矩阵，在解析数据先仅解析时间，通过时间判断其所对应的降频时间index位是否已经有对应的信号值，当没有对应的信号值时才解析数值并插入矩阵。通过避免不必要的数值解析转化从而降低CPU消耗、提升性能。
object1s()的实际实现就是 sampling(1000)

### 筛选信号解析
SDK支持使用数据时筛选仅需要的信号进行输出。这里需要特别说明的是，如果选择了信号，则只输出信号清单里所有数据不为空的情况。如果以上述的示例数据举例，用SQL的模式来表示。如果选择了 signal_10hz这个信号，则相当于执行了 

```
Select timestampe, signal_10hz from vsw where signal_10hz <> NULL
```

而并不是```Select timestampe, signal_10hz from vsw```

因此，如果选择了signal_10hz，最终的输出将是

timestamp.ms  | signal_10hz 
:-: | :-: 
1045 | 1001
1145 | 1002
1245 | 1003

## 高级场景

### 时间过滤
通过Factory的StartTime，EndTime两个参数可以指定数据的输出时间范围。缺省情况下，SDK将会输出VSW文件中所有的数据。在缺省的情况下，边缘端生成的单个VSW一般包括1分钟的数据，每30秒1个存储桶。在这种情况下，如果查询超过1个桶的数据指定开始时间和结束时间不会提升性能。但如果多个文件合并解析，或者从一个长时间范围且按时间范围分块的VSW中读取部分时间段数据，指定此两个参数将会大大提高数据查询的效率。

### 多文件合并解析
VDataReaderFactory类的输入setDataReader的参数是数组或是List类型，同一个车产生的连续VSW文件可以一起传入，VDataReader会自动根据VSW中的Bucket中的时间信息，对相应的VSW中的数据块进行排序后再进行解码输出。如果是多个车的VSW文件，则必须分开解析。如果放在一起解析，会产生难以预测的结果。

### 降频到1S
VDataFrame的object1s方法提供了降频到1S的功能。这个方法只保留读取到这一秒的第一条数据。如果要降频到其他的频率，可以直接调用sampling(1000)方法，参数是输出的时间隔，单位是毫秒。例如，这里填100则意味着每100毫秒保留一行最先读到的数据。如果没有，这个100毫秒的输出即为空。


### 复杂数据类型
TODO

# 完整代码示例
## VSW解析应用
- [vswdecode.py](src/vswdecode.py): 一个完整的将VSW文件解析成CSV的应用.
  - 支持输入文件路径和输出文件路径参数
  - 支持以base64编码过的vsw文件
  - 支持信号筛选参数
  - 支持填充、复杂类型扩展等参数

## VSW转ASC格式
- [vsw2asc.py](src/vsw2asc.py): 一个转Vector ASC格式的demo应用.
  - [ASCII Logging Files (.ASC)](https://support.vector.com/kb?id=kb_article_view&sysparm_article=KB0011536)  is an industry-stand Message-based format for reading and writing signal data. See [vsw2asc.py](src/vsw2asc.py) for a quick example on conversion.

## VSW转BLF格式
- [vsw2blf.py](src/vsw2blf.py): 一个转Vector BLF格式的demo应用.
  - [Binary Logging File (.BLF)](https://support.vector.com/kb?id=kb_article_view&sysparm_article=KB0011536)  is an industry-stand Message-based format for reading and writing signal data. 

# 示例数据文件
- [data_diff_freqency.vsw](data/vsw/data_diff_freqency.vsw): 示例数据文件内包含10Hz, 20Hz, 100Hz信号. 可以结合[vswdecode.py](src/vswdecode.py)和其他例子使用。
- [signal_2x2.vsw](data/vsw/signal_2x2.vsw): 示例CAN Data数据, 包括2个channel，每个channel有2个消息. 可以结合[vsw2asc.py](src/vsw2asc.py)和[vsw2blf.py](src/vsw2blf.py)使用。

# 获得帮助
如有任何问题或意见, 可以在[Github issues](https://github.com/exceeddata/sdk-vdata-python//issues)提出. EXCEEDDATA的商业客户可以联系[客服](mailto:support@smartsct.com).

## 贡献代码
我们欢迎所有的改进建议或代码.

<hr>

[回到目录](#目录)
