#!/usr/bin/env python
#coding: utf-8

import os, sys, re
import json
import requests
import time
import urllib2, base64
from socket import *

def checkTcpPort(host,port):
    result = int
    try:
        s = socket(AF_INET, SOCK_STREAM)
        s.settimeout(1)
        code = s.connect_ex((host,port))
        #print code
        s.close()
        result = code
    except Exception, e:
        result = 111
    return result

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
def zuzhuangData(tags = '', value = ''):
    endpoint = "172.16.10.99"
    metric = "userdefine"
    key = "remotetcpcheck"
    timestamp = int(time.time())
    step = 60
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
with open("./tcp.txt") as f:
    for line in f:
        results = re.findall("(\S+)",line)
        if len(results) != 4:
            pass
        else:
            print results
            host = results[0]
            port = int(results[1])
	    description = results[2]
	    projectname = results[3]
            tags = "project=ops,"
            tags += "host=%s,port=%s,description=%s,project=%s"%(host,port,description,projectname)
            value = checkTcpPort(host,port)
            p.append(zuzhuangData(tags,value))

print json.dumps(p, sort_keys=True,indent = 4)

uploadToAgent(p)
