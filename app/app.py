from flask import Flask, jsonify, request, render_template, redirect, url_for
from dotenv import load_dotenv
from pathlib import Path
import requests
import logging
import os
import time
import pickle
load_dotenv()

app = Flask("simple-iot-server")
app.logger.setLevel(logging.INFO)

# want ['hw-name', 'addr', 'path', option['air', 'on'], ['temp_upper', 27.5]]
# task save
send_tasks = {} #'hw-name':[['task-name', output_hw, 'path', option['air', 'on']], ...]
# >>> print(task)
# {'hw_a': [['task_a', 'path_a/', ['air', 'on'], ['temp_upper', 27.5]], ['task_b', 'path_b/', ['air', 'off'], ['temp_under', 20]]], 'hw_z': [['task_z', 'path_z/', ['tv', 'on'], [実行条件]], ['task_z2', 'path_z/', ['tv', 'off'], [実行条件]]]}

# hw save 
send_hw = {} #'hw-name':['addr', 'remote']
res_hw = {} #'hw-name':'temp'


# filesave
def file_load():
    try:
        with open("data/send_tasks.dict", "rb") as f:
            global send_tasks
            send_tasks = pickle.load(f)
    except:
        pass
    try:
        with open("data/send_hw.dict", "rb") as f:
            global send_hw
            send_hw = pickle.load(f)
    except:
        pass
    try:
        with open("data/res_hw.dict", "rb") as f:
            global res_hw
            res_hw = pickle.load(f)
    except:
        pass

def file_save():
    try:
        os.mkdir('data')
    except:
        pass

    f = Path("data/send_tasks.dict")
    f.touch(exist_ok=True)
    with open(f, "wb") as f:
        pickle.dump(send_tasks,f)

    f = Path("data/send_hw.dict")
    f.touch(exist_ok=True)
    with open(f, "wb") as f:
        pickle.dump(send_hw,f)
        
    f = Path("data/res_hw.dict")
    f.touch(exist_ok=True)
    with open(f, "wb") as f:
        pickle.dump(res_hw,f)

file_load()



@app.route("/")
def top():
    remote_control('http://172.30.200.4:32121/api/send', 'air', 'cancel')
    return jsonify({'status':'ok'}), 200

@app.route("/api/filesave/")
def data_save():
    file_save()
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
            app.logger.info(f"test!!!!!!!")
            tasks = send_tasks[name]
            for task in tasks:
                if (task[4][0] == 'temp_upper' and float(task[4][1]) < float(temp)) \
                    or (task[4][0] == 'temp_under' and float(task[4][1]) > float(temp)) \
                    or (task[4][0] == 'hum_upper' and float(task[4][1]) < float(hum)) \
                    or (task[4][0] == 'hum_under' and float(task[4][1]) > float(hum)):
                    run_send_task(task)
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
def run_send_task(task):
    try:
        task_name = task[0]
        hw_name = task[1]
        task_kind = send_hw[hw_name][1]
        addr = send_hw[hw_name][0]
        path = task[2]    
        option = task[3]
    except :
        app.logger.error('run_send_task: 引数が不正か、HW情報が存在しません')
        return True
    
    if task_kind == 'remote':
        remote_control(f"{addr}/{path}", option[0], option[1])
    else:
        app.logger.error('run_send_task: 該当処理が存在しません')
        return True
    return False

# is white-space
def isws(s:str) -> bool:
    return (not s) or s.isspace()


## WebUI
@app.route("/settings/")
def settings():    
    print(send_hw)
    return render_template('settings/index.html', out_hws=send_hw, in_hws=res_hw, rules=send_tasks)

@app.route("/settings/add-hw/", methods=["GET","POST"])
def add_hw():
    if request.method == 'GET':
        return render_template('settings/add-hw.html')
    elif request.method == 'POST':
        name = request.form.get('name')
        addr = request.form.get('addr')
        hw_type = request.form.get('hw-type')

        if isws(name) or isws(addr) or isws(hw_type):
            app.logger.info("add hw: フォームが空")
            return redirect(url_for('settings'))
        
        send_hw[name] = [addr, hw_type]
        app.logger.info(f"add_hw: {name},{addr},{hw_type}")
        return redirect(url_for('settings'))

@app.route("/settings/add-rule/", methods=["GET","POST"])
def add_rule():
    if request.method == 'GET':
        return render_template('settings/add-rule.html', out_hws=send_hw, in_hws=res_hw)
    elif request.method == 'POST':
        task_name = request.form.get('name')
        input_hw = request.form.get('input_hw')
        kind = request.form.get('kind')
        number = request.form.get('number')
        output_hw = request.form.get('output_hw')
        path = request.form.get('path')
        remote_name = request.form.get('remote_name') #Option
        remote_func = request.form.get('remote_func') #Option

        if isws(task_name) or isws(input_hw) or  isws(kind) or isws(number) or isws(output_hw) or isws(path) or isws(remote_name) or isws(remote_func):
            app.logger.info("add rule: フォームが空")
            return redirect(url_for('settings'))

        if send_tasks.get(input_hw) is not None:
            input_hw_temp = send_tasks.get(input_hw)
        else:
            input_hw_temp = []
        input_hw_temp.append([task_name, output_hw, path, [remote_name, remote_func], [kind, number]])
        send_tasks[input_hw] = input_hw_temp
        
        app.logger.info(f"add_rule: ")
        return redirect(url_for('settings'))

## App
def main():
    app.run(host='0.0.0.0', port=int(os.getenv('PORT')), threaded=True, debug=True)

if __name__ == '__main__':
    main()