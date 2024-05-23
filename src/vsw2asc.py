#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2016-2024 Smart Software for Car Technologies Inc. and EXCEEDDATA
#     https://www.smartsct.com
#     https://www.exceeddata.com
#
#                            MIT License
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. 
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY 
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, 
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE 
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# Except as contained in this notice, the name of a copyright holder
# shall not be used in advertising or otherwise to promote the sale, use 
# or other dealings in this Software without prior written authorization 
# of the copyright holder.
#
# Project: A demo application that converts vsw to asc format.
# Author:  Hongjun Shi

from datetime import datetime
from exceeddata.sdk.vdata import VDataReader, VDataByteReader
import can
from can import Message

#Input Data Sample file can be found sample_files/vsw/signal_2x2.vsw
#Signal data should be byte array and  stored in column name like {Channel_id}_{Frame_id}
#VSW文件中的信号名的格式为{Channel_id}_{Frame_id}，Channel id采用10进制表示，而Frame id采用0x开始的16进制表示
#More VSW files can be added to the inputPaths list for decode.
#示例中只有一个VSW文件，如果有多个VSW要合并转换的话，只需要在输入的文件名数组中继续添加
#Only 4 signals selected 0_0,0_1,1_0,1_1
#只选取了四组信号

inputPaths = ['../sample_files/vsw/signal_2x2.vsw']
seekables = []
signals = ['0_0', '0_1', '1_0', '1_1']
ascFilename='pycanasc.asc'

for fname in inputPaths:
    inFile = open(fname, "rb")
    data = inFile.read()
    seekables.append(VDataByteReader( data))

reader = VDataReader(seekables, signals=signals)
vdf = reader.df()

#print(vdf.cols)
#store the coloumn index to channel_id, message_id tuple mapping. 
#这里用来保留信号列与channel_id, message_id之间的对应关系，第一列总是为时间，所以会少一列
can_info= []
for signal in vdf.cols(): 
    arr = signal.split("_")
    if (len(arr)!= 2):
        can_info.append(None)
    else:
        #You can customize here for you own column name format.
        #这里需要做容错的处理，如果信号中有下划线，但不是数值就会出错。
        channel_id =int(arr[0])
        message_id = int (arr[1],base=16)
        can_info.append([channel_id,message_id])
        

current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print("  " + current_time)
ascwriter = can.ASCWriter(ascFilename)

#itorator for each row and data column.
#遍历解出来的每一行数据
for row in vdf.values():
    #第一列是时间，所以从第二列信号数据开始分析
    #time for first column, so we start from the second column.
    for i in range (1, len(row)):
            #如果信号非空，则生成相应的数据
            if row[i] != None:
                msg = Message(timestamp=row[0]/1000.0, channel=can_info[i-1][0],arbitration_id=can_info[i-1][1],data= row[i], is_fd=True)
                #写入ASC文件
                ascwriter.on_message_received(msg)

#finalize the ASC file and flush to disk
#将ASC文件终结，写入磁盘
ascwriter.stop()


