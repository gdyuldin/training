#!/usr/bin/env bash
PID=$(ps aux | grep daemon.py | head -n1 | awk '{ print $2 }')
lsof +p $PID | grep /tmp | head -n1 | awk '{{print $9}}'
