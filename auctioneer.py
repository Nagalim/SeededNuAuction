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
try:
  blkcnt = rpc.getblockcount()
except:
  print "Issues with RPC"
  sys.exit(1)

#Ask for Block Height of Auction Close
try:
  endblk = input('Enter Block Height of Auction Close: ')
  confirm = blkcnt - endblk
except:
  print "Please enter a 6 or 7 digit number like '384498'"
  sys.exit(1)
if confirm > 0:
  print "Auction ended",confirm,"blocks ago"
else:
  print "Auction close beyond downloaded blockchain.  Will proceed with all confirmed outputs."
  confirm=1

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
mynsr = (link[0])[1]
mynbt = (link[0])[0]


#Add addresses and amounts to the above initialed parameters for NBT deposits
for i in range(0,len(receivednbt)):
 packet = receivednbt[i]
 txid=packet['txid']
 tx=rpc.decoderawtransaction(rpc.getrawtransaction(txid))
 negamt=0
 for p in tx['vout']:
  chaddy=p['scriptPubKey']['addresses'][0]
  if chaddy != mynbt:
   negamt=negamt + p['value']
 addresses=[]
 for j in tx['vin']:
  input_raw_tx = rpc.decoderawtransaction(rpc.getrawtransaction(j['txid']))
  addy=input_raw_tx['vout'][j['vout']]['scriptPubKey']['addresses'][0]  
  amount=input_raw_tx['vout'][j['vout']]['value']
  #print "NBT receive:",addy," ",amount
  if negamt != 0:
   if amount > negamt:
    amount = amount - negamt
    negamt = 0
   else:
    negamt = negamt - amount
    amount = 0
  print "NBT receive:",addy," ",amount
  indices = [i for i, s in enumerate(link) if addy in s]
  if indices != []:
   if len(indices) == 1:
    pair=link[indices[0]]
    try:
     usersnsr[pair[1]] = usersnsr[pair[1]]+amount
    except:
     usersnsr[pair[1]] = amount
    nbttotal = nbttotal + amount
   else:
    print "More than one instance of",addy,"in addresses.txt"
    sys.exit(1)
  else:
   if not addy in usersnbt:
    usersnbtstore[addy] = amount
   else:
    usersnbtstore[addy] = usersnbtstore[addy] + amount

 
#Do the same with NSR deposits
for i in range(0,len(receivednsr)):
 packet = receivednsr[i]
 txid=packet['txid']
 tx=nsrrpc.decoderawtransaction(nsrrpc.getrawtransaction(txid))
 negamt=0
 for p in tx['vout']:
  chaddy=p['scriptPubKey']['addresses'][0]
  if chaddy != mynsr:
   negamt=negamt + p['value']
 addresses=[]
 for j in tx['vin']:
  input_raw_tx = nsrrpc.decoderawtransaction(nsrrpc.getrawtransaction(j['txid']))
  addy=input_raw_tx['vout'][j['vout']]['scriptPubKey']['addresses'][0]
  amount=input_raw_tx['vout'][j['vout']]['value']
  #print "NSR receive:",addy," ",amount
  if negamt != 0:
   if amount > negamt:
    amount = amount - negamt
    negamt = 0
   else:
    negamt = negamt - amount
    amount = 0
  print "NSR receive:",addy," ",amount
  indices = [i for i, s in enumerate(link) if addy in s]
  if indices != []:
   if len(indices) == 1:
    pair=link[indices[0]]
    try:
     usersnbt[pair[1]] = usersnbt[pair[1]]+amount
    except:
     usersnbt[pair[1]] = amount
    nsrtotal = nsrtotal + amount
   else:
    print "More than one instance of",addy,"in addresses.txt"
    sys.exit(1)
  else:
   if not addy in usersnsr:
    usersnsrstore[addy] = amount
   else:
    usersnsrstore[addy] = usersnsrstore[addy] + amount

#Totals and price
print 'Total Nbt Received:',nbttotal
print 'Total Nsr Received:',nsrtotal
price = max(nbttotal,0.001) / max(nsrtotal,1)
nbtprice = max(nbttotal-.02,0) / max(nsrtotal,1)
nsrprice = max(nbttotal,0) / max(nsrtotal-2,1)
print 'Auction Closing Price:',price,'NSR/NBT'

#Payout and Sendback
for i in usersnbt.iterkeys():
 usersnbt[i]=usersnbt[i]*nbtprice
for i in usersnsr.iterkeys():
 usersnsr[i]=usersnsr[i]/nsrprice
for i in usersnbtstore.iterkeys():
  usersnbt[i]=usersnbtstore[i]
for i in usersnsrstore.iterkeys():
  usersnsr[i]=usersnsrstore[i]

#Manysend Output
sumnbt=0
sumnsr=0
outnbt = {}
for addr in usersnbt:
  outnbt[addr] = float("%.8f" % usersnbt[addr])
  sumnbt = sumnbt + usersnbt[addr]
print "nud --unit=B sendmany", mynbt ,jsonrpc.dumps(outnbt).replace(' ', '')
outnsr = {}
for addr in usersnsr:
  outnsr[addr] = float("%.8f" % usersnsr[addr])
  sumnsr = sumnsr + usersnsr[addr]
print "nud sendmany", mynsr ,jsonrpc.dumps(outnsr).replace(' ', '')
print "Sum NBT to send:",sumnbt
print "Sum NSR to send:",sumnsr
