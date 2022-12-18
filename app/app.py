from flask import Flask, jsonify, request, render_template
from dotenv import load_dotenv
import requests
import logging
import os
import time
load_dotenv()

app = Flask("simple-iot-server")
app.logger.setLevel(logging.INFO)

# want ['hw-name', 'addr', 'path', option['air', 'on']]
# task save
send_tasks = {} #'hw-name':[['task-name', 'path', option['air', 'on']], ...]
# >>> print(task)
# {'hw_a': [['task_a', 'path_a/', ['air', 'on'], ['temp_upper', 27.5]], ['task_b', 'path_b/', ['air', 'off'], ['temp_under', 20]]], 'hw_z': [['task_z', 'path_z/', ['tv', 'on'], [実行条件]], ['task_z2', 'path_z/', ['tv', 'off'], [実行条件]]]}

# hw save 
send_hw = {} #'hw-name':['addr', 'remote']
res_hw = {} #'hw-name':'temp'



@app.route("/")
def top():
    # remote_control('http://172.30.200.4:32121/api/send', 'air', 'cancel')
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

        # 機材リストになければ送信元機材を追加
        if name not in res_hw:
            res_hw[str(name)] = 'temp'
            app.logger.info(f"add res_hw: {str(name)}")

        # TaskDictを確認して、あれば実行
        if name in send_tasks:
            tasks = send_tasks[name]
            for task in tasks:
                if (task[4][0] == 'temp_upper' and float(task[4][1]) < temp) \
                    or (task[4][0] == 'temp_under' and float(task[4][1]) > temp) \
                    or (task[4][0] == 'hum_upper' and float(task[4][1]) < hum) \
                    or (task[4][0] == 'hum_under' and float(task[4][1]) > hum):
                    run_send_task(name, task)
                    app.logger.info(f"run task: {task}")

        #app.logger.info(hum,temp)
        return jsonify({'status':'ok'}), 200

# API-RequestSend
def remote_control(addr=None, hw=None, func=None):
    if addr is None or hw is None or func is None:
        app.logger.error("RemoteControll: 引数が正しくありません")
        return True
    
    p = {'hw':hw, 'func':func}
    r = requests.get(addr, params=p)
    app.logger.info(f"RemoteControll: {r}")
    
    return False

# task executer
def run_send_task(hw_name, task):
    try:
        task_name = task[0]
        task_kind = send_hw[hw_name][1]
        addr = send_hw[hw_name][0]
        path = task[1]    
        option = task[3]
    except :
        app.logger.error('run_send_task: 引数が不正か、HW情報が存在しません')
        return True
    
    if task_kind == 'temp':
        remote_control(addr, option[0], option[1])
    else:
        app.logger.error('run_send_task: 該当処理が存在しません')
        return True
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