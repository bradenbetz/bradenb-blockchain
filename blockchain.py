import hashlib
import json
from time import time

"""
   This project was done to learn how a Blockchain functions on a technical level, to better understand how they work

"""


class Blockchain(object):

    # Initialize the Genesis Block and Current transaction
    def __init__(self):
        self.chain = []
        self.current_transactions = []

        # Create the Genesis(starting) block here
        self.new_block(previous_hash=1, proof=100)

    def new_block(self, proof, previous_hash=None):
        """
        Creates a new transaction to go into the next mined block
        :param previous_hash:
        :param proof: <int> The proof given by the proof of work algorithm
        :return: <dict> New block with transactions

        """
        block = {
            'index': len(self.chain),
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain(-1))
        }

        # Reset the current list of transactions on creation of a new block and add the block to the blockchain
        self.current_transactions = []
        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        """
        Creates a new transaction to go into the next mined block
        :param sender: <str> Address of the sender of the crypto
        :param recipient: <str> Address of the recipient of the crypto
        :param amount: <int> Amount of crypto being sent by the sender
        :return: <int> index of the block that will hold this transaction

        """
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })

        return self.last_block['index'] + 1

    @staticmethod
    def hash(block):
        """
        :param block: <dict> Block
        :return: <str> the hashed address

        """
        # The Dictionary must be ordered properly or the produced hashes will be inconsistent
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        return self.chain(-1)

