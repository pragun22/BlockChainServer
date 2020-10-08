from flask import Flask, request
from flask_httpauth import HTTPBasicAuth
from hashlib import sha256
import json
import time
import requests

auth = HTTPBasicAuth()

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
        return self._chain[-1]
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

server = Server()

@app.route('/auth', methods=['POST'])
def register():
    username = request.json.get('username')
    password = request.json.get('password')

    if username is None or password is None:
        abort(400)
    if server.alreadyExist(username):
        abort(400)

    data = {
        'user': username,
        'pass': password
    }
    block = Block(server.getLen(), data, time.time(), server.MostRecentBlock().hash, 0)

    proof = server.proofOfWork(block)

    server.add_block(block)
    return True

