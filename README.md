# SeededNuAuction
## A dual side, seedable auction protocol

To participate, read the config portion of participant.py and enter the appropriate information.


----------------------------------------------------------------------------------------------

Function and Method:

RPC operations take the auctioneer's wallet and process unspent transactions to find a common price.
It then outputs the target of a manysend command to be verified and sent manually by the auctioneer.
The target addresses are determined by pairs of NSR/NBT addresses ('links') in addresses.txt


Price = NBT received / NSR received

Each link receives funds:

NBT sent = NSR received * Price

NSR sent = NBT received / Price

Participants provide both NSR and NBT in a ratio corresponding to their ideal NBT/NSR price point.
Nu shareholders can vote on blockchain motions to seed this auction publicly in a verifiable manner.
All transactions are public on their respective blockchains, such that the auction must close precisely on a block.


Participant Instructions:
1.  Gather NBT and NSR you wish to submit to auction.  Note that the NBT/NSR ratio you submit can be identified as a virtual price.  If the auction closes on that price, your participation will be a wash.
2.  Move those NBT and NSR to 2 single addresses.  Single outputs even are ideal, but not necessary.
3.  Go find the auctioneer.  Tell them your NBT:NSR address pair.  Wish them well.  Ask them for the auction addresses and on what block the next auction closes.
4.  You can time your send to auction, or not (just be sure to get your txn in before it closes).  If you don't intend on gaming the auctions (this is to be encouraged!) then the timing doesn't matter.  Anyway, send using either coin control or the participant.py script presented here.  I'd suggest using coin control first with small amounts to make sure you know what's up and that you registered properly.
5.  Wait for the auction to close, your swapped funds should appear in your wallet after the auctioneer completes the manysend.



Auctioneer Instructions:
1.  Set up an empty NBT and NSR wallet.
2.  Grab a pair of NSR and NBT addresses in those wallets.  The RPC command is getnewaddress.
3.  Clone this repository.
4.  Stick that address pair at the first line in 'addresses.txt' ("Bxxx,Syyy").  The current addresses in there don't matter, they're just for show.
5.  Be your own participant at first, send some funds to the address pair using the 'Participant Instructions'.
6.  Run auctioneer.py and input a block height.  Check it out, try to get what's going on.
7.  Use the output of auctioneer.py to form a manysend RPC command for NBT and NSR individually.
8.  Tell everyone your address pair and get Nu onboard and let everyone know the ending block of the next auction.  You're now live!



Automation list:
Active recycling of unregistered txns
Error logging
Auction logging
Extra txn checking just in case (especially about the fees)
Crash cleanly if Nud fails
