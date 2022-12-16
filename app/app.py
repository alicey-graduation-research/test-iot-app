from flask import Flask, jsonify, request, render_template
from dotenv import load_dotenv
import logging
import os
import time
load_dotenv()

app = Flask("simple-iot-server")
app.logger.setLevel(logging.INFO)

tasks = {}

@app.route("/")
def top():
    return jsonify({'status':'ok'}), 200

## API
@app.route("/api/temp/", methods=["GET","POST"])
def temp():
    if request.method == 'GET':
        return jsonify({'status':'ok'}), 200
    elif request.method == 'POST':
        if request.headers['Content-Type'] != 'application/json':
            print(request.headers['Content-Type'])
            return jsonify(res='error'), 400
        name, hum, temp = request.json['name'], request.json['hum'], request.json['temp']
        app.logger.info(f"/temp[post]: name:{name}, hum:{hum}, temp:{temp}")

        #app.logger.info(hum,temp)
        return jsonify({'status':'ok'}), 200


## WebUI
@app.route("/settings/")
def settings():    
    return render_template('settings/index.html')


## App
def main():
    app.run(host='0.0.0.0', port=int(os.getenv('PORT')), threaded=True, debug=True)

if __name__ == '__main__':
    main()