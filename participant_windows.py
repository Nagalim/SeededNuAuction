#! /usr/bin/python

import jsonrpc
import sys, os
import time

#Configure RPC
NUCONFIG=r'C:\Users\**INSERTUSERNAMEHERE**\AppData\Roaming\Nu\nucoin.conf'
opts = dict(tuple(line.strip().replace(' ','').split('=')) for line in open(NUCONFIG).readlines())
try:
  rpc = jsonrpc.ServiceProxy("http://%s:%s@127.0.0.1:%s"%(
    opts['rpcuser'],opts['rpcpassword'],opts.pop('rpcport', 14002)))
except:
  print "could not connect to nbt daemon"
  sys.exit(1)
try:
  nsrrpc = jsonrpc.ServiceProxy("http://%s:%s@127.0.0.1:%s"%(
    opts['rpcuser'],opts['rpcpassword'],opts.pop('rpcport', 14001)))
except:
  print "could not connect to nsr daemon"
  sys.exit(1)
try:
  blkcnt = rpc.getblockcount()
except:
  print "Issues with RPC"
  sys.exit(1)


print "Successfully loaded Nu RPC and found block count as:",blkcnt
