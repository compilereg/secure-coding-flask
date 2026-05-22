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
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    
    return jsonify({"output": stdout.decode()})
    
    
###Endpoint to use SQL authentication
@app.route('/sqlauth', methods=['POST'])
def sqlauth():
    
    username = request.form.get('username')
    password = request.form.get('password')
    sql = f"SELECT * FROM users where (username = '{username}' and userpass = '{password}')"
    
    mycursor.execute(sql)

    try:
        result = mycursor.fetchone  ()
        if result:
            return jsonify({"Message": "Authenticated","sql": sql}),200
        else:
            return jsonify({"Message": "Authentication Failed","sql": sql}),401
    except mysql.connector.Error as err:
        msg = f"Error: {err} : {sql}"
        return jsonify({"error": msg}), 500 
            

###Endpoint to use Timed SQL injection to get all courses
@app.route('/timed', methods=['GET'])
def getcoursestimed():
    
    id = request.args.get('id')
    sql = f"SELECT * FROM courses where cid = {id}"
    
    mycursor.execute(sql)

    try:
        result = mycursor.fetchone  ()
        return jsonify({"Message": "Done"}),200
    except mysql.connector.Error as err:
        msg = f"Error: {err} : {sql}"
        return jsonify({"error": msg}), 500 

###Endpoint to use blind SQL injection to get all courses
@app.route('/blind', methods=['GET'])
def getcoursesblind():
    
    id = request.args.get('id')
    sql = f"SELECT * FROM courses where cid = {id}"
    
    
    mycursor.execute(sql)

    result = mycursor.fetchone  ()
    
    
    if result:  
        return jsonify({"Message": "Yes"}),200
    else:
        return jsonify({"Message": "No"}),500
    

##Endpoint consumes id after replacing the word select
@app.route('/getcourse1', methods=['GET'])
def getcourse1():
    
    id=request.args.get('id').replace("select", "")
    sql = f"SELECT * FROM courses WHERE cid = {id}"
    
    try:
        mycursor.execute(sql)
    except mysql.connector.Error as err:
        msg = f"Error: {err} : {sql}"
        return jsonify({"error": msg}), 500
    
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
    


##################Endpoint consumes the id as it come
@app.route('/getcourse', methods=['GET'])
def getcourse():
    
    id=request.args.get('id')
    sql = f"SELECT * FROM courses WHERE cid = {id}"
    
    mycursor.execute(sql)
    
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
    


if __name__ == '__main__':
    
    app.run(host="0.0.0.0" , port=5000, debug=True) 