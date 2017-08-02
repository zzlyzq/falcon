#!/usr/bin/env python
#coding: utf-8

import os, sys, re
import json
import requests
import time
import urllib2, base64
from socket import *

#os.chdir(os.path.dirname(os.path.realpath(__file__)))
print "Working dir is : %s"%os.getcwd()
os.chdir("c:\\windows-agent\\userdefine\\")
print "Working dir is : %s"%os.getcwd()

try:
    endpoint = sys.argv[1]
    step = sys.argv[2]
except:
    print "Usage: icmp.check.exe endpointAddress stepBySeconds"
    sys.exit()

#endpoint = "172.16.10.99"
#step = 300

def checkPing(host):
    #result = os.system("ping -i 0.1 -c 10 %s | tail -n 2 | tail -n 1 | awk -F\/ '{print $5}'"%host)
    #result=os.popen("ping -i 0.1 -c 10 %s | tail -n 2 | tail -n 1 | awk -F\/ '{print $5}'"%host).read()
    #result = os.popen("ping -i 0.1 -c 10 %s | tail -n 2 | tail -n 1 | awk -F\/ '{print $5}'" % host).read()
    #import pyping
    #r = pyping.ping(host, udp = 'True')
    import ping
    r = ping.quiet_ping(host,timeout=1,count=20)
    print r
    if r[0] == 100 :
        result = -1
    else:
       result = int(r[2])
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
def zuzhuangData(tags = '', value = '',endpoint = '172.16.10.99', step = 60 ):
    #endpoint = "172.16.10.99"
    metric = "userdefine"
    key = "icmp"
    timestamp = int(time.time())
    #step = 60
    vtype = "GAUGE"

    i = {
            'Metric' :'%s.%s'%(metric,key),
            'Endpoint': endpoint,
            'Timestamp': timestamp,
            'Step': int(step),
            'value': value,
            'CounterType': vtype,
            'TAGS': tags
            }
    return i

p = []
with open("./icmp.txt") as f:
    for line in f:
        results = re.findall("(\S+)",line)
        print results
        host = results[0]
        description = results[1]
        try:
            if len(results[2]) != 0:
                projectname = results[2]
            else:
                projectname = "ops"
        except:
            projectname = "ops"
        tags = ""
        tags += "host=%s,description=%s,project=%s"%(host,description,projectname)
        value = checkPing(host)
        p.append(zuzhuangData(tags,value,endpoint,step))

print json.dumps(p, sort_keys=True,indent = 4)

uploadToAgent(p)
