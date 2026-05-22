import hashlib
from flask import Flask, request, session, jsonify


#######################API login and logout with SHA-256 hashing and Flask sessions#######################


app = Flask(__name__)
app.config['SECRET_KEY'] = 'super-secret' 
UsersDB = {}

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']
    
    # DANGEROUS: SHA-256 is too fast; susceptible to GPU brute-forcing and rainbow tables
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    UsersDB[username] = hashed_password
    return jsonify({"message": "User registered"}), 201

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    hashed = hashlib.sha256(password.encode()).hexdigest()
    if (UsersDB.get(username) == hashed) :
        # Flask sets a cookie signed with 'super-secret'
        # Default flags miss critical browser protections
        session['user'] = username
        session['is_admin'] = False 
        return jsonify({"message": "Logged in"})
    
    return jsonify({"message": "Unauthorized"}), 401



print("Starting Flask application...")


if __name__ == '__main__':
    app.run(host="0.0.0.0" , port=5000, debug=True) 