import hashlib
from urllib import response
from flask import Flask, request, jsonify
import json               
from flask_jwt_extended import (
    create_access_token , JWTManager , jwt_required  , get_jwt_identity , get_jwt, set_access_cookies)


#######################API login and logout with SHA-256 hashing and Flask sessions#######################
##################Endpoint protected by JWT token authentication##################  
##################Uses cookies instead of authorization headers for JWT token storage, which is less secure##################



app = Flask(__name__ , static_folder='html')
    
app.config["JWT_SECRET_KEY"] = "secret"
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
app.config["JWT_COOKIE_SECURE"] = False  # Set to True in production (requires HTTPS)
app.config["JWT_ACCESS_COOKIE_NAME"] = "iticookie-new"
app.config["JWT_COOKIE_HTTPONLY"] = False
app.config['WTF_CSRF_ENABLED'] = False
app.config["SESSION_COOKIE_HTTPONLY"] = False
app.config["JWT_COOKIE_CSRF_PROTECT"] = True

#csrf = CSRFProtect(app)
    

app.config['SECRET_KEY'] = 'secret' 
UsersDB = {}
NewsDB = []


def createObject(u_id , u_news, u_author):
    return json.loads(json.dumps({"id": u_id, "news": u_news, "author": u_author}))

@app.route("/addnews",methods=['POST']) 
@jwt_required()
def addnews():
    news_id = request.form['id']
    news_content = request.form['news']
    news_author = get_jwt_identity()
    
    NewsDB.append(createObject(news_id,news_content,news_author))
    
    code = 201
    return jsonify({"message": "News added successfully"}),code

@app.route("/listnews",methods=['GET'])
@jwt_required()
def listnews():
    
               
    code = 200
    return NewsDB,code
    
    
    
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
        response = jsonify({"msg": "login successful"})
        response.set_cookie(
        'iticookie-new',            # Matches your JWT_ACCESS_COOKIE_NAME
        access_token,           # The string token value
        httponly=False,         # <-- CRITICAL: Forces the browser to keep it accessible to JS
        secure=False,           # Set to True only if running over local HTTPS
        samesite='Lax'
    )
            
        set_access_cookies(response, access_token)
         
        return response
    
    return jsonify({"message": "Unauthorized"}), 401



print("Starting Flask application...")


if __name__ == '__main__':
    UsersDB["admin"] = hashlib.sha256("adminpass".encode()).hexdigest()
    UsersDB["compiler"] = hashlib.sha256("userpass".encode()).hexdigest()
    
    NewsDB.append(createObject("1","news ID 1","admin"))
    NewsDB.append(createObject("2","news ID 2","admin"))

    jwt = JWTManager(app)
    
    app.run(host="0.0.0.0" , port=5000, debug=True) 
