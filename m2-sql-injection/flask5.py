from flask import Flask, request, jsonify
import mysql.connector
import os
import subprocess


#######################API login and logout with SHA-256 hashing and Flask sessions#######################
##################Endpoint protected by JWT token authentication##################  
##################Uses cookies instead of authorization headers for JWT token storage, which is less secure##################



app = Flask(__name__)
mydb = mysql.connector.connect(
  host="localhost",
  user="itiuser",
  password="itipass",
  database="itidb"
)

mycursor = mydb.cursor()

###Endpoint to ping a host
@app.route('/ping', methods=['GET'])
def ping():
    target_host = request.form.get('host')
    command = f"ping -c 1 {target_host}"
    process = subprocess.Popen(command, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    
    return jsonify({"output": stdout.decode()})
    
    
###Endpoint to use SQL authentication
@app.route('/sqlauth', methods=['POST'])
def sqlauth():
    
    username = request.form.get('username')
    password = request.form.get('password')
    sql = f"SELECT * FROM users where (username = %s and userpass = %s)"
    
    values = (username, password)
    
    mycursor.execute(sql,values)

    try:
        result = mycursor.fetchone  ()
        if result:
            return jsonify({"Message": "Authenticated","sql": sql}),200
        else:
            return jsonify({"Message": "Authentication Failed","sql": sql}),401
    except mysql.connector.Error as err:
        msg = f"Error: {err} : {sql}"
        return jsonify({"error": msg}), 500 
            

##################Endpoint consumes the id as it come
@app.route('/getcourse', methods=['GET'])
def getcourse():
    
    id=request.args.get('id')
    sql = f"SELECT * FROM courses WHERE cid = %s"
    values = (id,)
    try:
        mycursor.execute(sql,values)
    

        result = mycursor.fetchall  ()
        courses = []
        
        if result:
            for raw in result:       
                print(raw)
                course = {
                    "id": raw[0],
                    "name": raw[1],
                    "credithours": raw[2]
                }
                courses.append(course)
            
            return jsonify(courses)
        else:
            return jsonify({"error": "No courses found"}), 404
    except Exception as err:
        msg = f"Error: {err} : {sql}"
        return jsonify({"error": msg}), 500
    


if __name__ == '__main__':
    
    app.run(host="0.0.0.0" , port=5000, debug=True) 