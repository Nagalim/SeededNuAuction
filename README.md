# SeededNuAuction
A dual side, seedable auction protocol

To participate, read the config portion of participant.py and enter the appropriate information.




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

