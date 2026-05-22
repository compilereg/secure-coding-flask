import hashlib
from urllib import response
from flask import Flask, request, jsonify
from flask_jwt_extended import (
    create_access_token , JWTManager , jwt_required  , get_jwt_identity , get_jwt, set_access_cookies)
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman

#######################API login and logout with SHA-256 hashing and Flask sessions#######################
##################Endpoint protected by JWT token authentication##################  
##################Uses cookies instead of authorization headers for JWT token storage, which is less secure##################

                                                                                                                                            


app = Flask(__name__)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"], # Global fallback defaults
    storage_uri="memory://" # Use Redis in production, memory is perfect for labs
)

""" talisman = Talisman(
    app,
    force_https=True, 
    content_security_policy={
        'default-src': '\'self\'',
        'script-src': ['\'self\'', 'https://cdn.jsdelivr.net'] # Restricts script sources explicitly
    }
) """

app.config['SECRET_KEY'] = 'secret' 
UsersDB = {}

tickets_db = {
    "1": { "username": "compiler", "message": "Error in compiler app"},
    "2": { "username": "admin", "message": "Error in admin app"},
    "3": { "username": "khalid", "message": "Error in khalid app"},
    "4": { "username": "ayman", "message": "Error in ayman app"},
}


################Insecure url that load a ticket for a user
@app.route('/tickets/<ticket_id>', methods=['GET'])
@jwt_required()
def get_ticket(ticket_id):
    ticket = tickets_db.get(ticket_id)
    if not ticket:
        return jsonify({"error": "Ticket not found"}), 404
        
    # VULNERABLE: The API verifies the user is logged in (@jwt_required),
    # but NEVER checks if the logged-in user owns this specific ticket!
    return jsonify(ticket), 200

##############Secure url that load a ticket for a user
@app.route('/tickets_sec/<ticket_id>', methods=['GET'])
@jwt_required()
def get_ticket_sec(ticket_id):
    ticket = tickets_db.get(ticket_id)
    username = get_jwt_identity()
    
    if not ticket:
        return jsonify({"error": "Ticket not found"}), 404
    
    if ticket.get("username") != username:
        return jsonify({"error": "Access Denied: Unauthorized Object Reference"}), 403    
    # VULNERABLE: The API verifies the user is logged in (@jwt_required),
    # but NEVER checks if the logged-in user owns this specific ticket!
    return jsonify(ticket), 200


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

@app.route('/login_limit', methods=['POST'])
@limiter.limit("5 per minute", error_message="Too many login attempts. Try again in 60 seconds.")
def login_limit():
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
        response = jsonify({"msg": "login successful"})
        set_access_cookies(response, access_token)
         
        return response
    
    return jsonify({"message": "Unauthorized"}), 401


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
        response = jsonify({"msg": "login successful"})
        set_access_cookies(response, access_token)
         
        return response
    
    return jsonify({"message": "Unauthorized"}), 401


print("Starting Flask application...")


if __name__ == '__main__':
    UsersDB["admin"] = hashlib.sha256("adminpass".encode()).hexdigest()
    UsersDB["compiler"] = hashlib.sha256("userpass".encode()).hexdigest()
    UsersDB["khalid"] = hashlib.sha256("userpass".encode()).hexdigest()
    UsersDB["ayman"] = hashlib.sha256("userpass".encode()).hexdigest()
    
    
    app.config["JWT_SECRET_KEY"] = "secret"
    app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
    app.config["JWT_COOKIE_SECURE"] = False  # Set to True in production (requires HTTPS)
    app.config["JWT_ACCESS_COOKIE_NAME"] = "iticookie"
    
    
    jwt = JWTManager(app)
    
    
    app.run(host="0.0.0.0" , port=5000, debug=True) 