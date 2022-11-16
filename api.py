from crypt import methods
import hashlib
import json
from time import time
from uuid import uuid4
from block1 import BlockChain

from flask import Flask, jsonify, request

app = Flask(__name__)
# generates a globally unique address
node_identifier = str(uuid4()).replace("-", "")
# initiates the blockchain
blockchain = BlockChain()

@app.route('/mine', methods=['GET'])
def mine():
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    # send rewards to miner
    blockchain.new_transaction(
        sender=0,
        recipient=node_identifier,
        amount=1
    )

    # create the new block and add it to the chain
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': "Forged new block",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200

@app.route('/transaction/new', methods=['GET'])
def transaction_new():
    values = request.get_json()
    required = ['sender', 'recipient', 'amount']

    if not all(k in values for k in required):
        return "Missing values in the request", 400
    
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])
    response = {'message': f"Transaction will be added to the Block {index}"}
    return jsonify(response), 200

@app.route("/chain", methods=['GET'])
def chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }
    return jsonify(response), 200


@app.route('/miner/register', methods=['POST'])
def register_new_miner():
    values = request.get_json()

    # get the list of miner nodes
    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply list of valid nodes"
    
    for node in nodes:
        blockchain.register_miner_node(node)
    
    response = {
        "message": "New nodes have been added",
        "total_nodes": list(blockchain.nodes),
    }
    return jsonify(response), 200

@app.route('/miner/nodes/resolve', methods=['POSt'])
def consensus():
    conflicts = blockchain.resolve_conflicts()

    if conflicts:
        response = {
            'message': "Our chain was replaced",
            'new_chain': blockchain.chain,
        }
        return jsonify(response), 200
    
    response = {
        'message': "Our chain is authoritative",
        'chain': blockchain.chain,
    }
    return jsonify(response), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)