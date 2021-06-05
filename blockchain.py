import hashlib
import json
from time import time
from urllib.parse import urlparse
import requests

"""
   This project was done to learn how a Blockchain functions on a technical level, to better understand how they work

"""


class Blockchain(object):

    # Initialize the Genesis Block and Current transaction
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.nodes = set()

        # Create the Genesis(starting) block here
        self.new_block(previous_hash=1, proof=100)

    def register_node(self, address):
        """
        Add a new node(miner/computer) to the list of nodes
        :param address: Address of the node
        :return: None
        """

        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def valid_chain(self, chain):
        """
        Determine if the given blockchain is valid (Consensus Algorithm)
        :param chain: The blockchain to verify
        :return: <bool> True if valid, false if not
        """

        last_block = chain[0]
        current_index = 1
        # Can probably optimize this later
        while current_index < len(chain):
            block = chain[current_index]
            print(f'{last_block}')
            print(f'{block}')
            print("\n-----------\n")
            # Check that the hash of the block is correct
            if block['previous_hash'] != self.hash(last_block):
                return False

            # Check that the Proof-Of-Work is correct
            if not self.valid_proof(last_block['proof'], block['proof']):
                return False

            last_block = block
            current_index += 1

        return True

    def resolve_conflicts(self):
        """
        This is the consensus algorithm. It resolves conflicts with a given chain by replacing it by the longest one in
        the network.
        :return: <bool> True if the chain was replaced, False if not
        """

        neighbors = self.nodes
        new_chain = None

        # We are only looking for chains longer than the one our node currently holds

        max_length = len(self.chain)

        # Grab and verify the chains from all the nodes in our network

        for node in neighbors:
            response = requests.get(f'https://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                # Check if the length is longer and if the chain is valid
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        # Replace our chain if we discovered a new valid chain longer than the one our node holds
        if new_chain:
            self.chain = new_chain
            return True
        return False

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
        return self.chain[-1]

    def proof_of_work(self, last_proof):
        """
        The Proof Of Work Algorithim is as follows - Find a number p such that hash(pp') contains the leading 4 zeros, where p is the previous p'
        p is the previous proof and p' is the new proof
        :param last_proof: <int>
        :return: <int>
        """

        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1

        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        """
        Validates the proof, does the hash(last_proof, proof) contain the 4 leading zeros?
        :param last_proof: <int> Previous Proof
        :param proof: <int> Current Proof
        :return: <bool> True if correct, False if wrong
        """
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"
