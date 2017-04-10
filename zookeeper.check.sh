#!/bin/bash
# filename: zkmon

PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin:/root/bin

# 共享参数
endpoint="myip"

# 获取数据
echo stat | nc 127.0.0.1 myport > tmp.stat
echo wchs | nc 127.0.0.1 myport > tmp.wchs
echo ruok | nc 127.0.0.1 myport > tmp.ruok

# stat 命令的结果处理
zookeeper_stat_received=`cat tmp.stat | grep "Received:" | awk '{print $2}'`
zookeeper_stat_sent=`cat tmp.stat | grep "Sent:" | awk '{print $2}'`
zookeeper_stat_connections=`cat tmp.stat | grep "Connections:" | awk '{print $2}'`
zookeeper_stat_outstanding=`cat tmp.stat | grep "Outstanding:" | awk '{print $2}'`
zookeeper_stat_nodecount=`cat tmp.stat | grep "Node count:" | awk '{print $3}'`

# wchs 命令的结果处理
zookeeper_wchs_connections=`cat tmp.wchs | head -n1 | awk '{print $1}'`
zookeeper_wchs_watchingpaths=`cat tmp.wchs | head -n1 | awk '{print $4}'`
zookeeper_wchs_totalwatches=`cat tmp.wchs | grep 'Total watches' | awk -F\: '{print $2}'`

# ruok 命令的结果处理
zookeeper_ruok=`cat tmp.ruok | grep 'imok' | wc -l`

#echo $zookeeper_stat_received $zookeeper_stat_sent $zookeeper_stat_connections $zookeeper_stat_outstanding $zookeeper_stat_nodecount $zookeeper_wchs_connections $zookeeper_wchs_watchingpaths $zookeeper_wchs_totalwatches

# 最后删除临时文件
rm -f tmp.stat tmp.wchs tmp.ruok

# 数据上报
endpoint="myip"
timenow=`date +%s`

function upload() {
curl -X POST -H "Accept: application/json" -H "Content-Type: application/json" http://127.0.0.1:1988/v1/push -vv --data @<(cat <<EOF
[{
"metric": "$name", "endpoint": "$endpoint", "timestamp": $timenow, "step": 60,"value": "$value", "counterType": "$type", "tags": ""
}]
EOF
)
}

name="zookeeper_stat_received"
value="$zookeeper_stat_received"
type="COUNTER"
upload

name="zookeeper_stat_sent"
value="$zookeeper_stat_sent"
type="COUNTER"
upload

name="zookeeper_stat_connections"
value="$zookeeper_stat_connections"
type="GAUGE"
upload

name="zookeeper_stat_outstanding"
value="$zookeeper_stat_outstanding"
type="COUNTER"
upload

name="zookeeper_stat_nodecount"
value="$zookeeper_stat_nodecount"
type="GAUGE"
upload

name="zookeeper_wchs_connections"
value="$zookeeper_wchs_connections"
type="GAUGE"
upload

name="zookeeper_wchs_watchingpaths"
value="$zookeeper_wchs_watchingpaths"
type="GAUGE"
upload

name="zookeeper_wchs_totalwatches"
value="$zookeeper_wchs_totalwatches"
type="GAUGE"
upload

name="zookeeper_ruok"
value="$zookeeper_ruok"
type="GAUGE"
upload
