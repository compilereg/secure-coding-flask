from flask import Flask , request, jsonify
import requests
import os
from urllib.parse import urlparse

################################Application demonstrates the SSRF its fix
app = Flask(__name__ , static_folder='html')

print("Starting Flask application...")

NOTALLOWED = ["localhost","192.168.56.11"]


UPLOAD_FOLDER = os.path.abspath("public")


##################Insecure download causes Path traversal
@app.route('/readdata', methods=['POST'])
def get_remote_data():
    # Grabs the filename directly from the URL query string
    target_url = request.json.get('url')
    
    # VULNERABLE: The server blindly requests whatever URL the user provides
    try:
        response = requests.get(target_url, timeout=5)
        return jsonify({"status": "Success", "data": response.text}), 200
    except Exception as e:
        return jsonify({"status": "Error", "msg": str(e)}), 500
        
@app.route('/deletedb', methods=['GET'])
def remote_db():
        return jsonify("Database has been deleted"),200
    

##################Ssecure Path traversal
@app.route('/readdata_sec', methods=['POST'])
def get_remote_data_secure():
    target_url = request.json.get('url')
    parsed_url = urlparse(target_url)
    
    # 2. Match hostname against an denied not allowed list
    # Note:
    ## Send error message, destination domain is not allowed? or not found :-)
    
    if parsed_url.hostname in NOTALLOWED:
        return "Access Denied: destination domain not found", 404
        
    response = requests.get(target_url, timeout=5)
    return jsonify({"data": response.text})
    
    

        
if __name__ == '__main__':
   
    app.run(host="0.0.0.0" , port=5000, debug=True)