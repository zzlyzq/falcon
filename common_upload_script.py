#!/usr/bin/env python
#coding: utf8

import sys
import json
import requests
import time
import urllib2, base64
import commands

import eventlet
eventlet.monkey_patch()

# 获取数据
#r = requests.get('http://api.zc-us.mirahome.me:10086/ss')
#r2 = json.loads(r.text)
#value = r2['online']['total']
value = commands.getoutput("/usr/sbin/ss -ane | grep -i 'close-wait' | wc -l")

# 准备上报数据
p = []
endpoint = "172.16.72.34"
metric = "ss"
key = "closewait"
timestamp = int(time.time())
step = 60
vtype = "GAUGE"
tags = ''

i = {
        'Metric' :'%s.%s'%(metric,key),
        'Endpoint': endpoint,
        'Timestamp': timestamp,
        'Step': step,
        'value': value,
        'CounterType': vtype,
        'TAGS': tags
        }

p.append(i)

print json.dumps(p, sort_keys=True,indent = 4)

#sys.exit(0)

# 上报
method = "POST"
handler = urllib2.HTTPHandler()
opener = urllib2.build_opener(handler)
url = "http://127.0.0.1:1988/v1/push"
request = urllib2.Request(url, data=json.dumps(p))
request.add_header('Content-Type','application/json')
request.get_method = lambda: method
try:
    with eventlet.Timeout(3):
        connection = opener.open(request)
except urllib2.HTTPError,e:
    connection = e

if connection.code == 200:
    print connection.read()
else:
    print '{"err":1,"msg":"%s"}' % connection
