from flask import Flask, jsonify, request, render_template
from dotenv import load_dotenv
import requests
import logging
import os
import time
load_dotenv()

app = Flask("simple-iot-server")
app.logger.setLevel(logging.INFO)

tasks = {}

@app.route("/")
def top():
    remote_control('http://172.30.200.4:32121/api/send', 'air', 'cancel')
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

# API-RequestSend
def remote_control(addr=None, hw=None, func=None):
    if addr is None or hw is None or func is None:
        app.logger.info("RemoteControll: 引数が正しくありません")
        return True
    
    p = {'hw':hw, 'func':func}
    r = requests.get(addr, params=p)
    app.logger.info(f"RemoteControll: {r}")
    
    return False



## WebUI
@app.route("/settings/")
def settings():    
    return render_template('settings/index.html')


## App
def main():
    app.run(host='0.0.0.0', port=int(os.getenv('PORT')), threaded=True, debug=True)

if __name__ == '__main__':
    main()