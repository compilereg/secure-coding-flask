import hashlib
from flask import Flask, request, jsonify
from flask_jwt_extended import (
    create_access_token , JWTManager , jwt_required  , get_jwt_identity , get_jwt)



#######################API login and logout with SHA-256 hashing and Flask sessions#######################
##################Endpoint protected by JWT token authentication##################  


app = Flask(__name__)


app.config['SECRET_KEY'] = 'secret' 
UsersDB = {}


@app.route('/public', methods=['GET'])
def public():
    return jsonify({"message": "This is a public endpoint"})

@app.route('/priv', methods=['GET'])
@jwt_required()
def protected():
        claims = get_jwt()
        username = get_jwt_identity()
        userrole = claims.get("role")
        
        if userrole == "admin":
            msg    = f"Welcome  admin {username}"
        else:
            msg    = f"Welcome  user {username}"
        return jsonify({"message": msg})

    
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
        if username == "admin":
            user_role = "admin"
        else:
            user_role = "user"
        additional_claims = {"role": f"{user_role}"}
        access_token = create_access_token(identity=username,additional_claims=additional_claims)
         
        return jsonify({"message": "Logged in", "access_token": access_token})
    
    return jsonify({"message": "Unauthorized"}), 401



print("Starting Flask application...")


if __name__ == '__main__':
    UsersDB["admin"] = hashlib.sha256("adminpass".encode()).hexdigest()
    UsersDB["compiler"] = hashlib.sha256("userpass".encode()).hexdigest()
    
    app.config["JWT_SECRET_KEY"] = "secret"
    
    jwt = JWTManager(app)
    
    
    app.run(host="0.0.0.0" , port=5000, debug=True) 