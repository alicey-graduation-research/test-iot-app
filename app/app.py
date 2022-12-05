from flask import Flask, jsonify, request


app = Flask("simple-iot-server")

@app.route("/")
def top():
    return jsonify({'status':'ok'}), 200

@app.route("/temp/", methods=["GET","POST"])
def temp():
    if request.method == 'GET':
        return jsonify({'status':'ok'}), 200
    elif request.method == 'POST':
        return jsonify({'status':'ok'}), 200

def main():
    app.run(host='0.0.0.0', port=80, threaded=True)

if __name__ == '__main__':
    main()