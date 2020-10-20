from flask import Flask, render_template, request, redirect, send_from_directory, abort
# from flask_httpauth import HTTPBasicAuth
from hashlib import sha256
import json
import time
import requests
from flask_cors import CORS
# auth = HTTPBasicAuth()

class Block:
    def __init__(self, index, data, timestamp, prevhash, nonce = 0):
        self.index = index
        self.data = data
        self.timestamp = timestamp
        self.prevhash = prevhash
        self.nonce = nonce

    def compute_hash(self):
        BlockContent = json.dumps(self.__dict__, sort_keys=True)
        return sha256(BlockContent.encode()).hexdigest()

class Server:

    def __init__(self):
        self._chain = []
        self.difficulty = 2
        self.proof = sha256("First Block".encode()).hexdigest()

    def MostRecentBlockHash(self):
        if(len(self._chain) > 0):
            return self._chain[-1].hash()
        return sha256("First Block".encode()).hexdigest()

    def getLen(self):
        return len(self._chain)
    
    def isValid(self, block, blockHash):
        return (blockHash.startswith('0' *  self.difficulty) and blockHash == block.compute_hash())

    def add_block(self, block):
        prevhash = self.MostRecentBlockHash()
        x = sha256("First Block".encode()).hexdigest()
        print()
        if prevhash != block.prevhash:
            return False
        
        if x != prevhash and not self.isValid(block, self.proof):
            return False

        block.hash = self.proof
        self._chain.append(block)

    def alreadyExist(self, user):
        print("chain length", len(self._chain))
        for block in self._chain:
            if block.data['user'] == user:
                return True
        return False

    def auth(self, user, password):
    	for block in self._chain:
    		if block.data['user'] == user and block.data['password'] == password:
    			return True
    	return False

    def proofOfWork(self, block):
        block.nonce = 0
        
        computed_hash = block.compute_hash()
        while not computed_hash.startswith('0' * self.difficulty):
            block.nonce += 1
            computed_hash = block.compute_hash()

        return computed_hash

app = Flask(__name__)
HOST = '0.0.0.0'
PORT = 5000
CORS(app)
server = Server()

@app.route('/')
def hello():
	return render_template('home.html')

@app.route('/login', methods=['POST'])
def login():
    if(request.method == 'POST'):
        username = str(request.json.get('username'))
        password = str(request.json.get('password'))

        password = sha256(password.encode('utf-8')).hexdigest()

       	if server.auth(username, password):
            return "Success"
       		# return render_template('loggedIn.html')
       	else:
       		# return render_template('home.html')
            abort(400)
    abort(400)

@app.route('/register', methods=['POST'])
def register():
    if(request.method == 'POST'):
        username = str(request.json.get('username'))
        password = str(request.json.get('password'))

        if server.alreadyExist(username):
            # return render_template('loggedIn.html', msg = "User Already Registered")
            return "Success"
        password = sha256(password.encode('utf-8')).hexdigest() # Hashing the password
        data = {
            'type': 'info',
            'user': username,
            'password': password,
            'items' : [],
        }
        block = Block(server.getLen(), data, time.time(), server.MostRecentBlockHash(), 0)

        proof = server.proofOfWork(block)

        server.add_block(block)
        return "Success"
        # return render_template('loggedIn.html', msg = "Successfully Registered !")

    abort(400)
    # return render_template('home.html')


'''
For implementing Transaction feature we need features as follows:-

1. bet(buyer, seller, amount, item, txn_id/bet_id):
    this should send seller a notification for a possible buyer for his item (may need an database for this)
    We need to make bet such that a buyer shouldn't be able to make multiple bets even if he doesn't have sufficient
    coins to buy all of them 
2. accept(bet_id, buyer)
    this should send the buyer that the seller has accepted the price and now items belong to him
3. transact(buyer, seller, item, id)
    this function confirms the txn and adds to the block

Since we are using blockchain or openchain server we need to append items to item list and create a new block for them  

'''

@app.route('/buy/<buyer>/<seller>/<item>')
def bet(buyer, seller, item):
    txId = sha256(time.time() + seller + buyer)
    data = {
        'type' : 'bet',
        'buyer': buyer,
        'seller': seller,
        'item': item,
        'status' : 'onGoing'
    }
    block = Block(server.getLen(), data, time.time(), server.MostRecentBlockHash(), 0)
    proof = server.proofOfWork(block)
    server.add_block(block)
    # Add a function for sending notification below
    
    return
        

if __name__ == "__main__":
	app.run(host=HOST, port=PORT, debug=True)