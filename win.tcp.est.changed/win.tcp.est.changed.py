#!/usr/bin/env python
#coding: utf-8

import os, sys, re
import json
import requests
import time
import urllib2, base64
import re
from socket import *
#import pysed

#theServerAddressAndPort = "172.16.10.99:6030"
#myAddressAndPort = "192.168.10.104:62875"

try:
    endpoint = sys.argv[1]
    step = sys.argv[2]
except:
    print "Usage: xx.exe endpointAddress stepBySeconds"
    sys.exit()

def check(theServerAddressAndPort,myAddressAndPort):
    #result = os.system("ping -i 0.1 -c 10 %s | tail -n 2 | tail -n 1 | awk -F\/ '{print $5}'"%host)
    result=os.popen("""netstat -an | findstr "%s" | findstr "EST" """%theServerAddressAndPort).read()
    if len(result) > 0:
        theTargetString = re.findall("(\S+)",result)
        if theTargetString[1] == myAddressAndPort and theTargetString[2] == theServerAddressAndPort:
            # 0代表没有变化，正常。
            returnCode = 0
        else:
            # 1代表发生了变化，我们除了返回错误码1外，还需要修改一下下文件，达到下次自动记录的
            returnCode = 1
            # 我们需要修改文件了，先记录下日志
            import logging
            import logging.handlers
            LOG_FILE = 'win.tcp.est.changed.log'
            handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=1024 * 1024,backupCount=5)  # 实例化handler
            fmt = '%(asctime)s - %(filename)s:%(lineno)s - %(name)s - %(message)s'
            formatter = logging.Formatter(fmt)  # 实例化formatter
            handler.setFormatter(formatter)  # 为handler添加formatter
            logger = logging.getLogger('tst')  # 获取名为tst的logger
            logger.addHandler(handler)  # 为logger添加handler
            logger.setLevel(logging.DEBUG)
            logger.info(""" 发现异常，我们的期望是%s_%s， 但是找到了%s_%s """%(theServerAddressAndPort,myAddressAndPort,theTargetString[2],theTargetString[1]))
            # 修改文件
            #pysed.replace("win.tcp.est.changed.txt",myAddressAndPort,theTargetString[1])
            # Read in the file
            with open('win.tcp.est.changed.txt', 'r') as file:
                filedata = file.read()
            # Replace the target string
            filedata = filedata.replace(myAddressAndPort, theTargetString[1])
            # Write the file out again
            with open('win.tcp.est.changed.txt', 'w') as file:
                file.write(filedata)
            logger.info(""" 已经修改配置文件 """)
    else:
        # 2代表没有建立连接的发现
        returnCode = 1
    return returnCode

#check()
#sys.exit()

# 上报
def uploadToAgent(p):
    method = "POST"
    handler = urllib2.HTTPHandler()
    opener = urllib2.build_opener(handler)
    url = "http://127.0.0.1:1988/v1/push"
    request = urllib2.Request(url, data=json.dumps(p))
    request.add_header('Content-Type','application/json')
    request.get_method = lambda: method
    try:
        connection = opener.open(request)
    except urllib2.HTTPError,e:
        connection = e

    if connection.code == 200:
        print connection.read()
    else:
        print '{"err":1,"msg":"%s"}' % connection


print "开始 "

# 准备上报数据
def zuzhuangData(tags = '', value = '',endpoint = '172.16.10.99', step = 60):
    endpoint = endpoint
    metric = "userdefine"
    key = "win.tcp.est.changed"
    timestamp = int(time.time())
    #step = 60
    vtype = "GAUGE"

    i = {
            'Metric' :'%s.%s'%(metric,key),
            'Endpoint': endpoint,
            'Timestamp': timestamp,
            'Step': step,
            'value': value,
            'CounterType': vtype,
            'TAGS': tags
            }
    return i

p = []
with open("./win.tcp.est.changed.txt") as f:
    for line in f:
        results = re.findall("(\S+)",line)
        print results
        theServerAddressAndPort = results[0]
        myAddressAndPort = results[1]
        description = results[2]
        project = results[3]
        tags = "project=%s,"%project
        tags += "theServerAddressAndPort=%s,description=%s"%(theServerAddressAndPort,description)
        value = check(theServerAddressAndPort,myAddressAndPort)
        p.append(zuzhuangData(tags,value))

print json.dumps(p, sort_keys=True,indent = 4)

#uploadToAgent(p)
