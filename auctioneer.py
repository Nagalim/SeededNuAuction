#! /usr/bin/python

import jsonrpc
import sys, os

#Open addresses.txt
link = []
with open('addresses.txt') as inputfile:
    for line in inputfile:
        link.append(line.strip().split(','))

#Configure RPC
NUCONFIG='%s/.nu/nu.conf'%os.getenv("HOME")
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

#Ask for Block Height of Auction Close
try:
 endblk = input('Enter Block Height of Auction Close: ')
 blkcnt = rpc.getblockcount()
 confirm = blkcnt - endblk
 print "Auction ended ",confirm," blocks ago"
except:
 print "Please enter a 6 or 7 digit number like '384498'"
 sys.exit(1)

#Process unspent transactions
receivednbt = rpc.listunspent(confirm)
receivednsr = nsrrpc.listunspent(confirm)

#Initialize
nbttotal=0
nsrtotal=0
usersnbt = {}
usersnsr = {}
usersnbtstore = {}
usersnsrstore = {}

#Add addresses and amounts to the above initialed parameters for NBT deposits
for i in range(0,len(receivednbt)):
 packet = receivednbt[i]
 txid=packet['txid']
 tx=rpc.gettransaction(txid)
 trim=tx['details'][0]
 addy = trim['address']
 indices = [i for i, s in enumerate(link) if addy in s]
 if not addy in usersnsr:
  if indices != []:
   if len(indices) == 1:
    pair=link[indices[0]]
    usersnsr[pair[1]] = packet['amount']
    nbttotal = nbttotal + packet['amount']
   else:
    print "More than one instance of ",addy," in addresses.txt"
    sys.exit(1)
  else:
   usersnbtstore[addy] = packet['amount']
 else:
  if indices != []:
   pair=link[indices[0]]
   usersnsr[pair[1]] =  usersnsr[pair[1]] + packet['amount']
   nbttotal = nbttotal + packet['amount']
  else:
   usersnbtstore[addy] =  usersnbtstore[addy] + packet['amount']

#Do the same with NSR deposits
for i in range(0,len(receivednsr)):
 packet = receivednsr[i]
 txid=packet['txid']
 tx=nsrrpc.gettransaction(txid)
 trim=tx['details'][0]
 addy = trim['address']
 indices = [i for i, s in enumerate(link) if addy in s]
 if not addy in usersnbt:
  if indices != []:
   if len(indices) == 1:
    pair=link[indices[0]]
    usersnbt[pair[0]] = packet['amount']
    nsrtotal = nsrtotal + packet['amount']
   else:
    print "More than one instance of ",addy," in addresses.txt"
    sys.exit(1)
  else:
   usersnsrstore[addy] = packet['amount']
 else:
  if indices != []:
   pair=link[indices[0]]
   usersnbt[pair[0]] =  usersnbt[pair[0]] + packet['amount']
   nsrtotal = nsrtotal + packet['amount']
  else:
   usersnsrstore[addy] =  usersnbtstore[addy] + packet['amount']

#Totals and price
print 'Total Nbt Received:',nbttotal
print 'Total Nsr Received:',nsrtotal
price = max(nbttotal,0.001) / max(nsrtotal,1)
print 'Auction Closing Price:',price,'NSR/NBT'

#Payout and Sendback
for i in usersnbt.iterkeys():
 usersnbt[i]=usersnbt[i]*price
for i in usersnsr.iterkeys():
 usersnsr[i]=usersnsr[i]/price
for i in usersnbtstore.iterkeys():
  usersnbt[i]=usersnbtstore[i]
for i in usersnsrstore.iterkeys():
  usersnsr[i]=usersnsrstore[i]

#Manysend Output
outnbt = {}
for addr in usersnbt:
  outnbt[addr] = float("%.8f" % usersnbt[addr])
print jsonrpc.dumps(outnbt).replace(' ', '')
outnsr = {}
for addr in usersnsr:
  outnsr[addr] = float("%.8f" % usersnsr[addr])
print jsonrpc.dumps(outnsr).replace(' ', '')
