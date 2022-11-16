from hashlib import sha256
from urllib import request
from urllib.parse import urlparse
import hashlib
import json
import time
import requests

block2 = {
    'index': 1,
    'timestamp': 1506092455,
    'transactions': [
        {
            'sender': "852714982as982341a4b27ee00",
            'recipient': "a77f5cdfa2934hv25c7c7da5df1f",
            'amount': 5
        }
    ],
    'proof': 323454734020,
    'previous_hash': "2cf24dba5fb0a3202h2025c25e7304249898",
}

class BlockChain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.nodes = set()
        self.new_block(previous_hash=1, proof=100)

    @staticmethod
    def hash(block):
        # hashes a block
        block_string = json.dumps(block, sort_keys=True).encode()

        return hashlib.sha256(block_string).hexdigest()

    def new_block(self, proof, previous_hash):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time.time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),

        }
        self.current_transactions = []
        self.chain.append(block)
        return block

    @property
    def last_block(self):
        return self.chain[-1]
    
    def new_transaction(self, sender, recipient, amount):
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount
        })
        return self.last_block['index'] + 1
    
    def proof_of_work(self, last_proof):
        proof = 0
        while self.validate_proof(last_proof, proof) is False:
            proof += 1
        return proof
    
    @staticmethod
    def validate_proof(last_proof, proof):
        guess = f"{last_proof}{proof}".encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"
    
    def register_miner_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def valid_chain(self, chain):
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            if block['previous_hash'] != self.hash(last_block):
                return False
            if not self.validate_proof(last_block['proof'], block['proof']):
                return False
            
            last_block = block
            current_index += 1
        return True
    
    def resolve_conflicts(self):
        neighbors = self.nodes
        new_chain = None

        max_length = len(self.chain)

        for node in neighbors:
            response = requests.get(f"http://{node}/chain")

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain
        if new_chain:
            self.chain = new_chain
            return True
            
        return False