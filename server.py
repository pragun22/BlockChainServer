from flask import Flask, render_template, request, redirect, send_from_directory
# from flask_httpauth import HTTPBasicAuth
from hashlib import sha256
import json
import time
import requests

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

    def MostRecentBlock(self):
        if(len(self._chain) > 0):
            return self._chain[-1]
        return None
    def getLen(self):
        return len(self._chain)
    
    def isValid(self, block, blockHash):

        return (blockHash.startswith('0' *  self.difficulty) and blockHash == block.compute_hash())

    def add_block(self, block):
        prevhash = self.MostRecentBlock().hash

        if prevhash != block.prevhash:
            return False
        
        if not isValid(block, proof):
            return False

        block.hash = proof
        self._chain.append(block)

    def alreadyExist(self, user):
        for block in self._chain:
            if block.data.user == user:
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

server = Server()

@app.route('/')
def hello():
	return render_template('home.html')

@app.route('/login', methods=['POST'])
def login():
    if(request.method == 'POST'):
        username = str(request.form['username'])
        password = str(request.form['password'])
        return render_template('loggedIn.html', msg = "Successfully Logged In")
    return render_template('home.html')

@app.route('/register', methods=['POST'])
def register():
    if(request.method == 'POST'):
        username = str(request.form['username'])
        password = str(request.form['password'])

        if server.alreadyExist(username):
            return render_template('loggedIn.html', msg = "User Already Registered")

        data = {
            'user': username,
            'pass': password
        }
        block = Block(server.getLen(), data, time.time(), server.MostRecentBlock().hash, 0)

        proof = server.proofOfWork(block)

        server.add_block(block)
        return render_template('loggedIn.html', msg = "Successfully Registered !")
    return render_template('home.html')

if __name__ == "__main__":
	app.run(host=HOST, port=PORT, debug=True)