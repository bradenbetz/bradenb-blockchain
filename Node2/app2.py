from uuid import uuid4
from flask import Flask, jsonify, request
from Node2.blockchain2 import blockchain2

"""
App file that runs the uses the blockchain2 class to activate and run the blockchain2

ALL blockchain2 FUNCTIONS
http://localhost:5000/mine - Mines a new block  
http://localhost:5000/transactions/new - creates a new transaction
http://localhost:5000/chain - returns the current chain
http://localhost:5000/nodes/register - registers a new node
http://localhost:5000/nodes/resolve - resolves any discrepancies with the blockchain2

Initial NODE = http://localhost:5000
NODE 1 = http://localhost:5001
NODE 2 = http://localhost:5002
"""

# Instantiate the Node
app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the blockchain2
blockchain2 = blockchain2()


@app.route('/mine', methods=['GET'])
def mine():
    last_block = blockchain2.last_block
    proof = blockchain2.proof_of_work(last_block)

    blockchain2.new_transaction(
        sender="0",
        recipient=node_identifier,
        amount=1,
    )

    previous_hash = blockchain2.hash(last_block)
    block = blockchain2.new_block(proof, previous_hash)

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    index = blockchain2.new_transaction(values['sender'], values['recipient'], values['amount'])

    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain2.chain,
        'length': len(blockchain2.chain),
    }
    return jsonify(response), 200


@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json(force=True) # Added force=True to fix the Nonetype is not iterable

    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        blockchain2.register_node(node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain2.nodes),
    }
    return jsonify(response), 201


@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain2.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain2.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain2.chain
        }

    return jsonify(response), 200


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='0.0.0.0', port=port)

