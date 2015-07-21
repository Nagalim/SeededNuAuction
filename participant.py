import os
import sys
import jsonrpc
import time

#--------------------------Config-------------------------------#
# BACKUP YOUR WALLET BEFORE YOU USE THIS SOFTWARE!!!!!!!!!!!!!

nbtauc = 'BNjKzZtFtumiw3VNUVoWTNb8CoEtMZEEoN'
nsrauc = 'SMNjMt4Wu2DKbDavbP6FyxA6nv4ZWgdGEP'

# Hello!  Welcome to automated auctions where you name your price and volume.
# The code used here involves forging raw transactions and should not be taken lightly.
#
# Above, the two addresses should be public auction addresses.
#   If you are uncertain what those should be, please check discuss.nubits.com for the current auction addresses.
#
# Below, the two addresses are your registered participant addresses.
#   If you have not registered, simply send the pair of addresses to the auctioneer and wait for their reply giving you the go ahead.

nbtpar = ''
nsrpar = ''

# These are the auction parameters.  Volume is in units of nbt and 'price' is a NSR/NBT pricepoint.
#   'pw' is your encrypted wallet password.  Please be careful saving this on your computer.
volume  = 0.1
price= 0.0022
pw = ''

# Use APPDATA for Windows and HOME for Unix:
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


# Get transaction ID's
usnbt=rpc.listunspent(1,9999999,[nbtpar])
usnsr=nsrrpc.listunspent(1,9999999,[nsrpar])

# Prepare to forge nbt transaction
nbtfee=0.01
sumnbt=0
switchnbt=0
for t in range(0,len(usnbt)):
 if switchnbt==0:
  sumnbt+=usnbt[t]["amount"]
  if sumnbt+nbtfee >= volume:
   changenbt=sumnbt-volume-nbtfee
   switchnbt=1
  for k in usnbt[t].keys():
   if k == "account" or k == "amount" or k == "confirmations" or k == "address" or k == "scriptPubKey":
    del usnbt[t][k]
 else: usnbt.pop(t)

# Prepare to forge nsr transaction
nsrfee=1
sumnsr=0
switchnsr=0
nsrvolume=volume/price
for t in range(0,len(usnsr)):
 if switchnsr==0:
  sumnsr+=usnsr[t]["amount"]
  if sumnsr+nsrfee >= nsrvolume:
   changensr=sumnsr-nsrvolume-nsrfee
   switchnsr=1
  for k in usnsr[t].keys():
   if k == "account" or k == "amount" or k == "confirmations" or k == "address" or k == "scriptPubKey":
    del usnsr[t][k]
 else: usnsr.pop(t)

# Check that you have the funds
if sumnbt < volume + nbtfee or sumnsr < nsrvolume + nsrfee:
  sys.exit(1)
  
# Forge and send transactions
nbttxhsh=rpc.createrawtransaction(usnbt,{nbtauc:volume,nbtpar:changenbt})
nsrtxhsh=nsrrpc.createrawtransaction(usnsr,{nsrauc:nsrvolume,nsrpar:changensr})
rpc.walletpassphrase(pw,1)
nbttxsgn=rpc.signrawtransaction(nbttxhsh)
nsrtxsgn=nsrrpc.signrawtransaction(nsrtxhsh)

confirm = 'n'
confirm = raw_input('Are you sure you want to send:\n'+str({nbtauc:volume,nbtpar:changenbt})+'\n and \n'+str({nsrauc:nsrvolume,nsrpar:changensr})+'\n (Y/N)')

if confirm == 'y' or confirm == 'Y':
  rpc.walletpassphrase(pw,1)
  rpc.sendrawtransaction(nbttxsgn["hex"])
  nsrrpc.sendrawtransaction(nsrtxsgn["hex"])
else:
  sys.exit(1)


# Here's some teaser stuff for the future
#send=1000
#switch=0
#while True:
#  blkcnt = rpc.getblockcount()
#  if blkcnt%5000 > send and switch==0:
#
#
#    switch1=1
#  print blkcnt%5000
#  time.sleep(30)

