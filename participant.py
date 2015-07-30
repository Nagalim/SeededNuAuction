import os
import sys
import jsonrpc
import time
import urllib
import urllib2

#--------------------------Config-------------------------------#

nbtauc = 'BNjKzZtFtumiw3VNUVoWTNb8CoEtMZEEoN'
nsrauc = 'SMNjMt4Wu2DKbDavbP6FyxA6nv4ZWgdGEP'

# Hello!  Welcome to automated auctions where you name your price and volume.
# The code used here involves forging raw transactions and should not be taken lightly.
#
# Above, the two addresses should be public auction addresses.
#  If you are uncertain what those should be, please check discuss.nubits.com for the current auction addresses.
#
# Below, the two addresses are your registered participant addresses.
#  If you have not registered, simply send the pair of addresses to the auctioneer and wait for their reply giving you the go ahead.

nbtpar = ''
nsrpar = ''

# 'loop' is an integer corresponding to block number for repeated submission.  Use 'once' for a one time submission.
loop = 'once'
# 'volume' is a float corresponding to submission volume in NBT.
volume  = 0.1
# 'price' is the price used in conjunction with 'volume' to attain NSR submission volume.  Use 'market' for the price on Poloniex.
price= 'market'
# 'pw' is your encrypted wallet password.  Please be careful saving this on your computer.  If your wallet is unlocked, use ''
pw = ''

#Use APPDATA for Windows and HOME for Unix:
folder="APPDATA"
#folder="HOME"

#---------------------------Begin---------------------------------#

#Setting up RPC.
NUCONFIG=r'%s\nu\nu.conf'%os.getenv(folder)
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


#Get transaction ID's
def participate(nbtsuc,nsrauc,nbtpar,nsrpar,volume,price,pw,noobswitch):
 usnbt=rpc.listunspent(1,9999999,[nbtpar])
 usnsr=nsrrpc.listunspent(1,9999999,[nsrpar])
 if price == 'market':
   nsrprice = poloniex_query()
 else:
   nsrprice = price
 
 #Prepare to forge nbt transaction
 nbtfeemult = rpc.getinfo()['paytxfee']
 sumnbt = - 0.04 * nbtfeemult
 switchnbt=0
 for t in range(0,len(usnbt)):
  if switchnbt==0:
   sumnbt+=usnbt[t]["amount"]- 0.2*nbtfeemult
   if sumnbt+nbtfeemult >= volume:
    changenbt=sumnbt-volume-nbtfeemult
    switchnbt=1
   for k in usnbt[t].keys():
    if k == "account" or k == "amount" or k == "confirmations" or k == "address" or k == "scriptPubKey":
     del usnbt[t][k]
  else: usnbt.pop(t)    
 
 #Prepare to forge nsr transaction
 nsrfeemult = nsrrpc.getinfo()['paytxfee']
 sumnsr = -0.04 * nsrfeemult
 switchnsr=0
 nsrvolume=volume/nsrprice
 for t in range(0,len(usnsr)):
  if switchnsr==0:
   sumnsr+=usnsr[t]["amount"] - 0.2*nsrfeemult
   if sumnsr+nsrfeemult >= nsrvolume:
    changensr=sumnsr-nsrvolume-nsrfeemult
    switchnsr=1
   for k in usnsr[t].keys():
    if k == "account" or k == "amount" or k == "confirmations" or k == "address" or k == "scriptPubKey":
     del usnsr[t][k]
  else: usnsr.pop(t)  

 #Forge and send transactions
 nbttxhsh=rpc.createrawtransaction(usnbt,{nbtauc:volume,nbtpar:changenbt})
 nsrtxhsh=nsrrpc.createrawtransaction(usnsr,{nsrauc:nsrvolume,nsrpar:changensr})
 if pw != '':
  rpc.walletpassphrase(pw,1)
 nbttxsgn=rpc.signrawtransaction(nbttxhsh)
 nsrtxsgn=nsrrpc.signrawtransaction(nsrtxhsh)
 if noobswitch==1:
  confirm = 'n'
  confirm = raw_input('Are you sure you want to send:\n'+str({nbtauc:volume,nbtpar:changenbt})+'\n and \n'+str({nsrauc:nsrvolume,nsrpar:changensr})+'\n (Y/N)')
  if confirm == 'y' or confirm == 'Y':
   rpc.sendrawtransaction(nbttxsgn["hex"])
   nsrrpc.sendrawtransaction(nsrtxsgn["hex"])
   noobswitch = 0
  else:
   sys.exit(1)
 else:
   rpc.sendrawtransaction(nbttxsgn["hex"])
   nsrrpc.sendrawtransaction(nsrtxsgn["hex"]) 

def poloniex_query():
 try: # bitfinex
  ret = jsonrpc.loads(urllib2.urlopen(urllib2.Request('https://api.bitfinex.com/v1//pubticker/btcusd'), timeout = 3).read())
  btcprice = float(ret['mid'])
 except:
  try: # coinbase
   ret = jsonrpc.loads(urllib2.urlopen(urllib2.Request('https://coinbase.com/api/v1/prices/spot_rate?currency=USD'), timeout = 3).read())
   btcprice = float(ret['amount'])
  except:
   try: # bitstamp
    ret = jsonrpc.loads(urllib2.urlopen(urllib2.Request('https://www.bitstamp.net/api/ticker/'), timeout = 3).read())
    btcprice = float(ret['bid'])
   except:
    print 'unable to update price for BTC'
    sys.exit(1)
 try: # poloniex
  ret = jsonrpc.loads(urllib2.urlopen(urllib2.Request('https://poloniex.com/public?command=returnTicker'),timeout=3).read())['BTC_NSR']
  newpoloprice = btcprice * (float(ret['last']) + float(ret['highestBid']) + float(ret['lowestAsk']) + 0.5*float(ret['high24hr']) + 0.5*float(ret['low24hr']))/4
  #ret = jsonrpc.loads(urllib2.urlopen(urllib2.Request('https://poloniex.com/public?command=return24hVolume'),timeout=3).read())['BTC_NSR']
  #polo_vol = ret['BTC']
 except:
  print 'unable to update price for NSR'
  sys.exit(1)
 #try:
 #ret = jsonrpc.loads(urllib2.urlopen(urllib2.Request('http://data.bter.com/api/1/ticker/nsr_btc'),timeout=3).read())
 #newbterprice = btcprice * (float(ret['last']) + float(ret['sell']) + float(ret['buy']) + 0.5*float(ret['high']) + 0.5*float(ret['low']))/4
 #bter_vol = ret['vol_btc']
 #except:
 # print 'unable to update price for NSR'
 # sys.exit(1)
 #newprice = newpoloprice * 0.75 + newbterprice * 0.25
 #print polo_vol, bter_vol
 return newpoloprice

#Loop twice a minute
noobswitch = 1
if loop != 'once':
 switch=0
 while True:
  blkcnt = rpc.getblockcount()
  if blkcnt%5000 > loop and switch==0:
   participate(nbtauc,nsrauc,nbtpar,nsrpar,volume,price,pw,noobswitch)
   switch=1
  time.sleep(30)
else:
 participate(nbtauc,nsrauc,nbtpar,nsrpar,volume,price,pw,noobswitch)

