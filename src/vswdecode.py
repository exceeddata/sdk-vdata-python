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
# Project: A full sample application on using the SDK to decode vsw data.
# Author:  Nick Xie
# Usage:   python3 vswdecode.py -i input_path -o output_path [-s names] [-b true|false] [-f true|false] [-d #] [-m last|first|all] [-p none|flat|full]

from exceeddata.sdk.vdata import VDataReaderFactory, VDataByteReader
import pandas as _pd
import getopt, sys
import base64

def str2bool(v):
    if not v:
        return False
    return not v.lower() in ("false", "0", "no")

def printUsage():
    print("python3 vswdecode.py [...]")
    print("  [-i|input <paths>]. Required. The input vsw file path(s). Multiple files are comma separated.")
    print("  [-o|output <path>]. Required. The output file path.")
    print("  [-s|signals <names>]. Optional. Comma-separated list of signal names to extract.")
    print("  [-b|base64 <true|false>]. Optional. Whether the input file is base64 encoded. Default is false.")
    print("  [-f|formula <true|false>]. Optional. Whether to apply signal formula.  Default is true.")
    print("  [-d|densify <#>]. Optional. The number of rows to look ahead to fill in for initial null rows.  Default is 0 (no fill in)")
    print("  [-m|qmode <last|first|all>]. Optional. The retrieve mode when there are multiple values for a signal at the same time. Default is 'last' (use last value)")
    print("  [-p|expand <none|flat|full>]. Optional. 'none' is output as columns as stored. 'flat' will extract structs into individual columns. 'full' is extract with qualified name. Default is 'full')")
    print("  [-h|help]. optional)")

args = sys.argv[1:]
argopts = "hi:o:s:b:f:d:m:p:"

try:
    ks, vs = getopt.getopt(args, argopts)
except Exception as e:
    emsg = str(e)
    try:
        print('Error' + emsg[emsg.index(':'):])
    except ValueError:
        print('Error: ' + emsg)
    printUsage()
    exit()

inputPaths = ''
outputPath = ''
signalNames = ''
base64Encoded = False
densifyRowsAhead = 0    # change to positive number to prefill (make dense) by looking ahead the specified number of rows
densifyOutputItv = 0    # change to positive number to output at a specified millisecond frequency
signalQueueRows = 0
signalQueueMode = None  # change to "first", "last", or "all" if there are multiple values at the same time

for k, v in ks:
    if (k == "-h"):
        printUsage()
        exit()
    elif (k == "-i"):
        inputPaths = str(v).strip()
    elif (k == "-o"):
        outputPath = str(v).strip()
    elif (k == "-s"):
        signalNames = str(v).strip()
    elif (k == '-b'):
        base64Encoded = str2bool(str(v).strip())
    elif (k == '-d'):
        densifyRowsAhead = int(str(v).strip())
    elif (k =='-m'):
        signalQueueMode = str(v).strip()

if len(inputPaths) == 0:
    print("Error: input path parameter empty")
    printUsage()
    exit()
if len(outputPath) == 0:
    print("Error: output path parameter empty")
    printUsage()
    exit()

df = None
reader = None
seekables = []
cols = {}
inputs = inputPaths.split(',')
signals = signalNames.split(',') if len(signalNames) > 0 else []

for p in inputs:
    if (len(p.strip()) > 0):
        inFile = open(p.strip(), "rb")
        data = inFile.read()
        seekables.append(VDataByteReader(base64.b64decode(data) if base64Encoded else data))
        inFile.close()

if (len(seekables) == 0):
    print("Error: no valid input paths")
    exit()

rfactory = VDataReaderFactory()
rfactory.setDataReaders(seekables)
rfactory.setSignals(signals)
reader = rfactory.open()       
frame = reader.df()

# choose one of the following method, frame.cols(True) will return column names with time at first index
# df = _pd.DataFrame(frame.values(), columns=frame.cols(True))
# df = _pd.DataFrame(frame.values(densifyRowsAhead, densifyOutputItv, signalQueueRows), columns=frame.cols(True))
# df = _pd.DataFrame(frame.objects(), columns=frame.cols(True))
# df = _pd.DataFrame(frame.objects(densifyRowsAhead, densifyOutputItv), columns=frame.cols(True))
# df = _pd.DataFrame(frame.object1s(), columns=frame.cols(True))

df = _pd.DataFrame(frame.objects(), columns=frame.cols(True))

# uncomment to cleanse and pretty the df for csv output
# df = df.fillna('')
# df = df.astype(str)
# df = df.replace(to_replace = "\.0+$", value = "", regex = True)

# output to csv
df.to_csv(outputPath, header=True, index=False)
