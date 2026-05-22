from flask import Flask , request, send_file, abort
import os
from werkzeug.utils import secure_filename

################################Application demonstrates the Path traversal and its fix
app = Flask(__name__ , static_folder='html')

print("Starting Flask application...")



UPLOAD_FOLDER = os.path.abspath("public")


##################Insecure download causes Path traversal
@app.route('/download', methods=['GET'])
def vulnerable_download():
    # Grabs the filename directly from the URL query string
    filename = request.args.get('file')
    
    # VULNERABLE: Direct string concatenation allows directory escaping
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    
    if os.path.exists(file_path):
        return send_file(file_path)
    else:
        abort(404)
        
        
#################Secure download
@app.route('/download_secure', methods=['GET'])
def secure_download():
    filename = request.args.get('file')
    
    # FIX A: Strip out all directory traversal sequences (e.g., '../../passwd' becomes 'passwd')
    safe_filename = secure_filename(filename)
    
    print(f"file: {safe_filename}")
    
    file_path = os.path.join(UPLOAD_FOLDER, safe_filename)
    
    # FIX B (Defense in Depth): Explicit path confinement validation
    # Check that the real, absolute path actually starts with the base folder path
    abs_base = os.path.abspath(UPLOAD_FOLDER)
    abs_target = os.path.abspath(file_path)
    
    if not abs_target.startswith(abs_base):
        return "Access Denied: Path Traversal Detected", 403
        
    return send_file(abs_target)

        
if __name__ == '__main__':
   
    app.run(host="0.0.0.0" , port=5000, debug=True)