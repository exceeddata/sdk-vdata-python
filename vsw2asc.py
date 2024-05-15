
from datetime import datetime
from exceeddata.sdk.vdata import VDataReader, VDataByteReader
import can
from can import Message

#本示例展示的是将存储在VSW中的原始信号帧数据输出到ASC文件中的例子
#VSW文件中的信号名的格式为{Channel_id}_{Frame_id}，Channel id采用10进制表示，而Frame id采用0x开始的16进制表示
#示例中只有一个VSW文件，如果有多个VSW要合并转换的话，只需要在输入的文件名数组中继续添加
#只选取了四组信号

inputPaths = ['EXD_file_signal0.vsw']
seekables = []
signals = ['3_0x268', '3_0x32c', '3_0x338', '3_0x3a2']
ascFilename='pycanasc.asc'

for fname in inputPaths:
    inFile = open(fname, "rb")
    data = inFile.read()
    seekables.append(VDataByteReader( data))

reader = VDataReader(seekables, signals=signals)
vdf = reader.df()

#print(vdf.cols)
#这里用来保留信号列与channel_id, message_id之间的对应关系，第一列总是为时间，所以会少一列
can_info= []
for signal in vdf.cols(): 
    arr = signal.split("_")
    if (len(arr)!= 2):
        can_info.append(None)
    else:
        #这里需要做容错的处理，如果信号中有下划线，但不是数值就会出错。
        channel_id =int(arr[0])
        message_id = int (arr[1],base=16)
        can_info.append([channel_id,message_id])
        

current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print("  " + current_time)
ascwriter = can.ASCWriter(ascFilename)

#遍历解出来的每一行数据
for row in vdf.values():
    #第一列是时间，所以从第二列信号数据开始分析
    for i in range (1, len(row)):
            #如果信号非空，则生成相应的数据
            if row[i] != None:
                msg = Message(timestamp=row[0]/1000.0, channel=can_info[i-1][0],arbitration_id=can_info[i-1][1],data= row[i], is_fd=True)
                #写入ASC文件
                ascwriter.on_message_received(msg)

#将ASC文件终结，写入磁盘
ascwriter.stop()


