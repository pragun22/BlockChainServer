from flask import Flask, render_template, request, redirect, send_from_directory
# from flask_httpauth import HTTPBasicAuth
from hashlib import sha256
import json
import time
import requests
from copy import deepcopy
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
            return self._chain[-1].hash
        return sha256("First Block".encode()).hexdigest()

    def getLen(self):
        return len(self._chain)
    
    # def isValid(self, block, blockHash):
    #     return (blockHash.startswith('0' *  self.difficulty) and blockHash == block.compute_hash())

    def add_block(self, block):
        prevhash = self.MostRecentBlockHash()
        x = sha256("First Block".encode()).hexdigest()
        # print()
        if prevhash != block.prevhash:
            return False
        
        # if x != prevhash and not self.isValid(block, self.proof):
        #     return False

        block.hash = self.proof
        self._chain.append(block)

    def alreadyExist(self, user):
        # print("chain length", len(self._chain))
        for block in self._chain[::-1]:
            if block.data['username'] == user:
                return True, block.data
        return False, {}
    
    def print_chain(self):
        for block in self._chain:
            print(block.data)
            print()

    def auth(self, user, password):
    	for block in self._chain:
    		if block.data['username'] == user and block.data['password'] == password:
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

        password = sha256(password.encode()).hexdigest()

       	if server.auth(username, password):
       		return render_template('loggedIn.html', msg = "Logged in")
       	else:
       		return render_template('loggedIn.html', msg = "Invalid Info")
    return render_template('home.html')

@app.route('/register', methods=['POST'])
def register():
    if(request.method == 'POST'):
        email = 'a@c'
        # email = str(request.form['email'])
        username = str(request.form['username'])
        password = str(request.form['password'])

        if server.alreadyExist(username)[0]:
            return render_template('loggedIn.html', msg = "User Already Registered")
        password = sha256(password.encode()).hexdigest() # Hashing the password
        data = {
            "type" : "info",
            "email": email,
            "username": username,
            "password" : password,
            "attributes" : {
                "level": "2",
                "next_task": "bjcsdr4543r4bhvhv4m2",
                "xp_points": "420",
                "coins": "0",
                "cash": "1"
            },
            "inventory": {
                "number_of_items": "3",
                "items": [
                    {
                        "name": "abcd",
                        "quantity": "1",
                        "type": "coins",
                        "auction": "",
                        "price": "123",
                        "isBiding": "true"
                    },
                    {
                        "name": "sfd",
                        "quantity": "2",
                        "type": "scroll",
                        "auction": "",
                        "price": "123",
                        "isBiding": "true"
                    }
                ]
            }
        }
        block = Block(server.getLen(), data, time.time(), server.MostRecentBlockHash(), 0)

        proof = server.proofOfWork(block)

        server.add_block(block)
        return render_template('loggedIn.html', msg = "Successfully Registered !")

    return render_template('home.html')

@app.route('/userInfo', methods=['POST'])
def getPlayerInfo():
    content = request.get_json() # might be wrong
    # content = {
    #    username : "",
    # }
    return server.alreadyExist(content['username'])[1]

@app.route('/debugFunc', methods=['POST'])
def debugFunc():
    print("before updating")
    server.print_chain()
    data = {
        'username' : 'a',
        "attributes" : {
            "level": "3",
            "next_task": "bjcsdr4543r4bhvhv4m2",
            "xp_points": "7000",
            "coins": "10",
            "cash": "10"
        },
        'items' : [
            {
                "name": "abcd",
                "quantity": "4",
                "type": "coins",
                "auction": "",
                "price": "123",
                "isBiding": "true"
            },
            {
                "name": "xyz",
                "quantity": "2",
                "type": "coins",
                "auction": "",
                "price": "123",
                "isBiding": "true"
            },
        ],
        'operation' : 'add',
    }

    update_user(data)
    print("\n\nafter updating 1")
    server.print_chain()
    data = {
        'username' : 'a',
        "attributes" : {
            "level": "3",
            "next_task": "bjcsdr4543r4bhvhv4m2",
            "xp_points": "7000",
            "coins": "10",
            "cash": "10"
        },
        'items' : [
            {
                "name": "xyz",
                "quantity": "1",
                "type": "coins",
                "auction": "",
                "price": "123",
                "isBiding": "true"
            },
        ],
        'operation' : 'delete',
    }
    update_user(data)
    print("\n\nafter updating 2 ")
    server.print_chain()
    update_user(data)
    print("\n\nafter updating 3")
    server.print_chain()
    return render_template("loggedIn.html", msg = {"phoddaaa"})

@app.route('/update', methods=['POST'])
def update_user(content):
    # getting json object from frontend
    # content = request.get_json() # might be wrong
    # content = {
    #    username : "",
    #    items : [item1, item2],
    #    attributes: {
    #    }
    #    operation : add/delete,
    # }
    user_data = deepcopy(server.alreadyExist(content['username'])[1])
    user_data['attributes'] = content['attributes']
    if content['operation'] == "add" :
        for item in content['items']:
            fl = 1
            for exist_item in user_data['inventory']['items']:
                if item['name'] == exist_item['name']:
                    exist_item['quantity'] = str(int(exist_item['quantity']) + int(item['quantity']))
                    fl = 0
                    break
            if fl == 1:
                user_data['inventory']['items'].append(item)
        
        user_data['inventory']['number_of_items'] = str(len(user_data['inventory']['items']))
    
    elif  content['operation'] == "delete" :
        lst = []
        for exist_item in user_data['inventory']['items']:
            fl = 1
            for item in content['items']:
                if item['name'] == exist_item['name']:
                    exist_item['quantity'] = str(int(exist_item['quantity']) - int(item['quantity']))
                    if int(exist_item['quantity']) != 0 :
                        lst.append(exist_item)
                    fl = 0
                    break
            if fl == 1:
                lst.append(exist_item)

        user_data['inventory']['items'] = lst
        user_data['inventory']['number_of_items'] = str(len(lst))
    else :
        return

    block = Block(server.getLen(), user_data, time.time(), server.MostRecentBlockHash(), 0)
    server.add_block(block)




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
